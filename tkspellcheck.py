from Tkinter import *
from ttk import *
from ScrolledText import ScrolledText
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter, HTMLChunker

class ModifiedText(ScrolledText):
    """http://code.activestate.com/recipes/464635-call-a-callback-when-a-tkintertext-is-modified/"""
    def __init__(self, root, *args, **kwargs):
        self.root = root

        self.spellcheck_enabled = kwargs.pop('spellcheck_enabled', True)
        lang = kwargs.pop('language', 'en_US')
        filters = kwargs.pop('filters', [EmailFilter, URLFilter])
        chunkers = kwargs.pop('chunkers', (HTMLChunker,))
        self.checker = SpellChecker(lang=lang, filters=filters, chunkers=chunkers)

        ScrolledText.__init__(self, self.root, *args, **kwargs)

        self._reset_alert_flag()
        self.bind('<<Modified>>', self._txtevt)

        if self.spellcheck_enabled:
            self.enable_spellcheck()

    def enable_spellcheck(self):
        self.spellcheck_enabled = True
        self.tag_remove('spellingerr', '1.0', 'end')
        self._check_spelling('1.0', END)
        self._reset_alert_flag()

    def disable_spellcheck(self):
        self.spellcheck_enabled = False
        self.tag_remove('spellingerr', '1.0', 'end')
        self._reset_alert_flag()

    def reload(self):
        if self.spellcheck_enabled:
            self.enable_spellcheck()

    def fire_on_textevent(self):
        pass

    def fire_spellcheck(self):
        if self.spellcheck_enabled:
            startpos, endpos = self._findposition()
            self._check_spelling(startpos, endpos)

    def _txtevt(self, evt):
        if not self._resetting_alert_flag:
            self._reset_alert_flag()
            self.fire_on_textevent()

    def _reset_alert_flag(self):
        """http://epydoc.sourceforge.net/stdlib/Tkinter.Text-class.html#edit_modified"""
        self._resetting_alert_flag = True
        self.edit_modified(False)
        self._resetting_alert_flag = False

    def _findposition(self):
        startpos = '{0}.0'.format(int(self.index(INSERT).split('.')[0]) - 1)
        endpos = '{0}.0'.format(int(self.index(INSERT).split('.')[0]) + 1)
        return (startpos, endpos)

    def _check_spelling(self, startpos, endpos):
        pos = startpos
        self.tag_remove('spellingerr', startpos, endpos)
        self.checker.set_text(self._get_text(startpos, endpos))
        for e in self.checker:
            begintag, endtag = self._wordposition(e.word, pos, endpos)
            self._tag_word(begintag, endtag)
            pos = endtag

    def _tag_word(self, begintag, endtag):
        self.tag_config('spellingerr', background="yellow", underline=False)
        self.mark_set('left-spellingerr', begintag)
        self.mark_set('right-spellingerr', endtag)
        self.mark_gravity('left-spellingerr', LEFT)
        self.mark_gravity('right-spellingerr', RIGHT)
        self.tag_add('spellingerr', 'left-spellingerr', 'right-spellingerr')
        self.tag_bind('spellingerr', '<Button-3>', self._get_suggestions)

    def _wordposition(self, word, startsearch, endsearch):
        starts = self.search(word, startsearch, endsearch)
        ends = starts + ('+%dchars' % len(word))
        return (starts, ends)

    def _get_text(self, startpos, endpos):
        return self.get(startpos, endpos)

    def _get_suggestions(self, evt):
        self.mark_set('insert', 'current')
        startpos = self.index('insert wordstart')
        endpos = self.index('insert wordend')
        suggested = self._suggest(self.get(startpos, endpos))
        context_menu = self._generate_contextmenu(startpos, endpos, suggested)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def _suggest(self, e):
        return self.checker.suggest(e)

    def _generate_contextmenu(self, startpos, endpos, suggested):
        contextmenu = Menu(self, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda startpos=startpos,
                                    endpos=endpos, word=word:
                                    self._replace(startpos, endpos, word))
        return contextmenu

    def _replace(self, startpos, endpos, word):
        self.delete(startpos, endpos)
        self.insert(startpos, word)
        self.mark_unset('left-spellingerr', startpos)
        self.mark_unset('right-spellingerr', endpos)
        self.tag_remove('spellingerr', startpos, endpos)

