import tk
from ScrolledText import ScrolledText
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter, HTMLChunker

class ContextAwareTxt(ScrolledText):
    """http://code.activestate.com/recipes/464635-call-a-callback-when-a-tkintertext-is-modified/"""
    def __init__(self, master, **kw):
        ScrolledText.__init__(self, master, **kw)
        self.initialize_alerts()

    def initialize_alerts(self):
        self._reset_alert_flag()
        self.bind('<<Modified>>', self._alert_modified)
        self.bind('<<Cut>>', self._alert_cut)
        self.bind('<<Paste>>', self._alert_paste)

    def terminate_alerts(self):
        self.bind('<<Modified>>', self._apathetic)
        self.bind('<<Cut>>', self._apathetic)
        self.bind('<<Paste>>', self._apathetic)

    def _alert_modified(self, event):
        if not self._resetting_alert_flag:
            self._reset_alert_flag()
            self.fire_on_modified(event)

    def _alert_cut(self, event):
        self.fire_on_cut(event)

    def _alert_paste(self, event):
        self.fire_on_paste(event)

    def _reset_alert_flag(self):
        """http://epydoc.sourceforge.net/stdlib/Tkinter.Text-class.html#edit_modified"""
        self._resetting_alert_flag = True
        self.edit_modified(False)
        self._resetting_alert_flag = False

    def _apathetic(self, event=None):
        pass

    def _setup_spellcheckr(self):
        self.spellingerrors = {}
        self.counter = 0
        self.checker = SpellChecker(self.lang, filters=[EmailFilter, URLFilter], chunkers=[HTMLChunker])

    def fire_on_textevent(self, event=None):
        #self.after_idle(self._fire)
        #self.after(100, self._fire)
        self._fire()

    def _fire(self):
        print "_fire!"
        startpos, endpos = self._findposition()
        self._check_spelling(startpos, endpos)

    def _findposition(self):
        currentline = int(self.index(tk.INSERT).split('.')[0])
        start = currentline - 1
        end = currentline + 1
        startpos = '{0}.0'.format(start)
        endpos = '{0}.0'.format(end)
        return (startpos, endpos)

    def _check_spelling(self, startpos, endpos):
        currentpos = startpos
        self._clear_tags(startpos, endpos)
        text = self._get_text(startpos, endpos)
        self.checker.set_text(text)
        for err in self.checker:
            begintag, endtag = self._wordposition(err.word, currentpos, endpos)
            self._tag_word(err.word, begintag, endtag)
            self.counter += 1
            currentpos = endtag

    def _tag_word(self, word, begintag, endtag):
        tag = '{0}-{1}'.format(word, self.counter)
        markleft = 'left-{0}'.format(tag)
        markright = 'right-{0}'.format(tag)
        self.tag_config(tag, background="yellow", foreground="red", underline=True)
        self.mark_set(markleft, begintag)
        self.mark_set(markright, endtag)
        self.mark_gravity(markleft, tk.LEFT)
        self.mark_gravity(markright, tk.RIGHT)
        self.tag_add(tag, markleft, markright)
        self.tag_bind(tag, '<Button-3>', lambda evt,
                      tag=tag: self._get_suggestions(evt, tag))
        self.spellingerrors[tag] = (word, markleft, markright, self.counter)

    def _wordposition(self, word, startsearch, endsearch):
        starts = self.search(word, startsearch, endsearch)
        ends = starts + ('+%dchars' % len(word))
        return (starts, ends)

    def _get_text(self, startpos, endpos):
        return self.get(startpos, endpos)

    def _get_suggestions(self, evt, tag):
        err = self.spellingerrors[tag][0]
        suggested = self._suggest(err)
        context_menu = self._generate_contextmenu(tag, suggested)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def _suggest(self, err):
        return self.checker.suggest(err)

    def _generate_contextmenu(self, tag, suggested):
        contextmenu = tk.Menu(self, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda tag=tag,
                                    word=word: self._replace(tag, word))
        return contextmenu

    def _replace(self, tag, word):
        firstpos, lastpos = self._tagranges(tag)
        self.delete(firstpos, lastpos)
        self.insert(firstpos, word)
        self._delete_tag(tag)

    def _tagranges(self, tag):
        return self.tag_ranges(tag)

    def _clear_tags(self, startpos, endpos):
        for tag in self.spellingerrors.keys():
            self.tag_remove(tag, startpos, endpos)

    def _delete_tag(self, tag):
        left = self.spellingerrors[tag][1]
        right = self.spellingerrors[tag][2]
        self.mark_unset(left)
        self.mark_unset(right)
        self.tag_delete(tag)
        del self.spellingerrors[tag]

    def _delete_all_tags(self):
        for tag in self.spellingerrors.keys():
            self._delete_tag(tag)

class SpellCheck(object):
    def __init__(self, **kw):
        self.spellingerrors = {}
        self.counter = 0
        self._lang = kw.get('lang', 'en_US')
        self._filtr = kw.get('filters', [EmailFilter, URLFilter])
        self._chunkr = kw.get('chunkers', [HTMLChunker])
        self.checker = SpellChecker(self._lang, filters=self._filtr, chunkers=self._chunkr)

    def check(self, text):
        sorry_slick = []
        self.checker.set_text(text)
        for fuckyou in self.checker:
            sorry_slick.append(fuckyou.word)
        return sorry_slick