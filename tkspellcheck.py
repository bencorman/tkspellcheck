from Tkinter import Text, Menu, RIGHT, LEFT, END
from ttk import *
import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter, HTMLChunker
import time


class AlertMixin(object):

    def initialize_alerts(self):
        self.reset_flag()
        self.bind('<<Modified>>', self._textevent)

    def _textevent(self, event=None):
        if not self._flag_reset:
            self.reset_flag()
            self.fire_on_alert(event)

    def fire_on_alert(self, event=None):
        pass

    def reset_flag(self):
        """http://epydoc.sourceforge.net/stdlib/Tkinter.Text-class.html#edit_modified"""
        self._flag_reset = True
        self.edit_modified(False)
        self._flag_reset = False


class CkTxt(AlertMixin, Text):
    def __init__(self, master=None, cnf={}, **kw):
        Text.__init__(self, master, cnf, **kw)

    def enable(self, lang='en_US'):
        self.spellingerrors = {}
        self.suggest_words = enchant.Dict(lang)
        self.checker = SpellChecker(lang, filters=[EmailFilter, URLFilter], chunkers=[HTMLChunker])
        self.counter = 0
        self._firstcheck()
        self.initialize_alerts()

    def disable(self):
        self._clear_tags()
        self._clearbindings()

    def _clearbindings(self):
        self.bind('<<Modified>>', lambda e: None)

    def fire_on_alert(self, event=None):
        start = time.time()
        self.after_idle(self._fire)
        ttime = (time.time() - start)
        print ttime

    def _fire(self):
        self._clear_tags()
        self._check()

    def _firstcheck(self):
        self._check()

    def _check(self):
        curpos = '1.0'
        text = self.get('1.0', END)
        self.checker.set_text(text)
        for err in self.checker:
            firstpos = self.search(err.word, curpos, END)
            lastpos = firstpos + ('+%dchars' % len(err.word))
            tag = '{0}-{1}'.format(err.word, self.counter)
            markleft = 'left-{0}'.format(tag)
            markright = 'right-{0}'.format(tag)
            self.tag_config(tag, background="yellow", foreground="red", underline=True)
            self.mark_set(markleft, firstpos)
            self.mark_set(markright, lastpos)
            self.mark_gravity(markleft, LEFT)
            self.mark_gravity(markright, RIGHT)
            self.tag_add(tag, markleft, markright)
            self.tag_add(tag, firstpos, lastpos)
            self.tag_bind(tag, '<Button-3>', lambda evt,
                          tag=tag: self._get_suggestions(evt, tag))
            self.spellingerrors[tag] = (err.word, markleft, markright,
                                        self.counter)
            self.counter += 1
            curpos = lastpos

    def _get_suggestions(self, evt, tag):
        err = self.spellingerrors[tag][0]
        suggested = self._suggest(err)
        context_menu = self._generate_contextmenu(tag, suggested)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def _suggest(self, err):
        return self.suggest_words.suggest(err)

    def _generate_contextmenu(self, tag, suggested):
        contextmenu = Menu(self, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda tag=tag,
                                    word=word: self._replace(tag, word))
        return contextmenu

    def _replace(self, tag, word):
        firstpos, lastpos = self._tagranges(tag)
        self.delete(firstpos, lastpos)
        self.insert(firstpos, word)

    def _tagranges(self, tag):
        return self.tag_ranges(tag)

    def _delete_tag(self, tag):
        self.tag_delete(tag)
        for i in (self.spellingerrors[tag][1], self.spellingerrors[tag][2]):
            self.mark_unset(i)
        del self.spellingerrors[tag]

    def _clear_tags(self):
        for tag in self.spellingerrors.keys():
            self._delete_tag(tag)
