from Tkinter import *
from ttk import *
import enchant
from enchant.checker import SpellChecker


class tkSpellCheck(Text):
    def __init__(self, master=None, cnf={}, **kw):
        Text.__init__(self, master, cnf, **kw)

    def spellcheck(self, lang='en_US', usrdict=[]):
        self.suggwords = enchant.Dict(lang)
        self.checker = SpellChecker(lang)
        self.spellingerrors = {}
        self.__initialcheck()

    def fullcheck(self):
        self.__cleartags()
        text = self.__alltxt()
        self.__settags(text, 1.0, END)

    def __initialcheck(self):
        self.fullcheck()
        self.bind('<space>', self.__check)

    def __check(self, evt):
        startpos = self.index('insert linestart')
        endpos = self.index('insert lineend')
        text = self.__linetxt(startpos, endpos)
        self.__settags(text, startpos=startpos, endpos=endpos)

    def __settags(self, text, startpos, endpos):
        i = 1
        curpos = startpos
        self.checker.set_text(text)
        for err in self.checker:
            firstltr = self.search(err.word, curpos, endpos)
            lastltr = firstltr + ('+%dchars' % len(err.word))
            if not self.__istagged(firstltr):
                tag = '{0}-{1}'.format(err.word, i)
                markleft = 'ml-{0}'.format(tag)
                markright = 'mr-{0}'.format(tag)
                self.tag_config(tag, foreground="red", underline=True)
                self.mark_set(markleft, firstltr)
                self.mark_set(markright, lastltr)
                self.mark_gravity(markleft, LEFT)
                self.mark_gravity(markright, RIGHT)
                self.tag_add(tag, markleft, markright)
                self.tag_add(tag, firstltr, lastltr)
                self.tag_bind(tag, '<Button-3>', lambda evt,
                              tag=tag: self.__suggestedwords(evt, tag))
                i += 1
                self.spellingerrors[tag] = (err.word, markleft, markright)
            curpos = lastltr

    def __istagged(self, idx):
        tag = self.tag_names(idx)
        if tag in self.spellingerrors.keys():
            return True
        else:
            return False

    def __suggestedwords(self, evt, tag):
        err = self.spellingerrors[tag][0]
        suggwords = self.__suggest(err)
        context_menu = self.__contextmenu(tag, suggwords)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def __cleartags(self):
        for tag in self.spellingerrors.keys():
            self.__deltag(tag)

    def __clearbindings(self):
        self.bind('<space>', lambda e: None)

    def __deltag(self, tag):
        self.tag_delete(tag)
        for i in (self.spellingerrors[tag][1], self.spellingerrors[tag][2]):
            self.mark_unset(i)
        del self.spellingerrors[tag]

    def __alltxt(self):
        return self.get(1.0, END)

    def __linetxt(self, startpos, endpos):
        return self.get(startpos, endpos)

    def __suggest(self, err):
        return self.suggwords.suggest(err)

    def __contextmenu(self, tag, suggested):
        err = self.spellingerrors[tag][0]
        contextmenu = Menu(self, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda tag=tag,
                                    word=word: self.__replace(tag, word))
        contextmenu.add_separator()
        contextmenu.add_command(label='Add to Dictionary', command=lambda
                                err=err: self.__usrdict(err))
        return contextmenu

    def __tagranges(self, tag):
        return self.tag_ranges(tag)

    def __replace(self, tag, word):
        firstltr, lastltr = self.__tagranges(tag)
        self.delete(firstltr, lastltr)
        self.insert(firstltr, word)
        self.__deltag(tag)

    def __usrdict(self, err):
        '''TODO: Add a personal dictionary file '''
        pass

if __name__ == '__main__':
    main()
