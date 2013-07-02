from Tkinter import *
from ttk import *
import enchant
from enchant.checker import SpellChecker


class tkSpellCheck:
    def __init__(self, textwidget, lang='en_US'):
        self.txtwdgt = textwidget
        self.suggwords = enchant.Dict(lang)
        self.checker = SpellChecker(lang)
        self.spellerrs = {}

    def __call__(self, disable=False):
        if disable:
            self.__cleartags()
            self.__clearbindings()
        else:
            self.__setup()

    def __setup(self):
        self.__fullcheck()
        self.txtwdgt.bind('<space>', self.__spellcheck())

    def __fullcheck(self):
        self.__cleartags()
        text = self.__alltxt()
        self.__settags(text, 1.0, END)

    def __spellcheck(self):
        startpos = self.txtwdgt.index('insert linestart')
        endpos = self.txtwdgt.index('insert lineend')
        text = self.__linetxt(startpos, endpos)
        self.__settags(text, startpos=startpos, endpos=endpos)

    def __settags(self, text, startpos, endpos):
        i = 1
        curpos = startpos
        self.checker.set_text(text)
        for err in self.checker:
            firstltr = self.txtwdgt.search(err.word, curpos, endpos)
            lastltr = firstltr + ('+%dchars' % len(err.word))
            if not self.__istagged(firstltr):
                tag = '{0}-{1}'.format(err.word, i)
                markleft = 'ml-{0}'.format(tag)
                markright = 'ml-{0}'.format(tag)
                self.txtwdgt.tag_config(tag, foreground="red", underline=True)
                self.txtwdgt.mark_set(markleft, firstltr)
                self.txtwdgt.mark_set(markright, lastltr)
                self.txtwdgt.mark_gravity(markleft, LEFT)
                self.txtwdgt.mark_gravity(markright, RIGHT)
                self.txtwdgt.tag_add(tag, markleft, markright)
                self.txtwdgt.tag_bind(tag, '<Button-3>', lambda evt,
                                      tag=tag: self.__suggestedwords(evt, tag))
                i += 1
                self.spellerrs[tag] = (err.word, markleft, markright)
            curpos = lastltr

    def __istagged(self, idx):
        tag = self.txtwdgt.tag_names(idx)
        if tag in self.spellerrs.keys():
            return True
        else:
            return False

    def __suggestedwords(self, evt, tag):
        err = self.spellerrs[tag][0]
        suggwords = self.__suggest(err)
        context_menu = self.__contextmenu(tag, suggwords)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def __clearalltags(self):
        for tag in self.spellerrs.keys():
            self.__deltag(tag)

    def __clearbindings(self):
        self.txtwdgt.bind('<space>', lambda e: None)

    def __deltag(self, tag):
        self.txtwdgt.tag_delete(tag)
        for i in (self.spellerrs[tag][1], self.spellerrs[tag][2]):
            self.txtwdgt.mark_unset(i)
        del self.spellerrs[tag]

    def __alltxt(self):
        return self.txtwdgt.get(1.0, END)

    def __linetxt(self, startpos, endpos):
        return self.txtwdgt.get(startpos, endpos)

    def __suggest(self, err):
        return self.suggwords.suggest(err)

    def __contextmenu(self, tag, suggested):
        err = self.spellerrs[tag][0]
        contextmenu = Menu(self.txtwdgt, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda tag=tag,
                                    word=word: self.__replace(tag, word))
        contextmenu.add_separator()
        contextmenu.add_command(label='Add to Dictionary', command=lambda
                                err=err: self.__usrdict(err))
        return contextmenu

    def __tagranges(self, tag):
        return self.txtwdgt.tag_ranges(tag)

    def __replace(self, tag, word):
        firstltr, lastltr = self.__tagranges(tag)
        err = self.spellerrs[tag][0]
        self.txtwdgt.delete(firstltr, lastltr)
        self.txtwdgt.insert(firstltr, word)
        self.__deltag(tag)

    def __usrdict(self, err):
        '''TODO: Add a personal dictionary file '''
        pass

if __name__ == '__main__':
    main()
