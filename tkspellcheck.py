from Tkinter import *
from ttk import *
import enchant
from enchant.checker import SpellChecker


class tkSpellCheck:
    def __init__(self, textwidget, lang='en_US'):
        self.textwidget = textwidget
        self.suggwords = enchant.Dict(lang)
        self.checker = SpellChecker(lang)
        self.spellerrs = {}

    def __call__(self, mode=False):
        if mode == 'fullcheck':
            self.fullcheck()
        if mode == 'inline':
            self.inlinecheck()
        if not mode:
            self.remove_tags()

    def fullcheck(self):
        self.__clearalltags()
        text = self.__alltxt()
        self.__settags(text, startpos='1.0', endpos='END')

    def inlinecheck(self):
        startpos = self.textwidget.index('insert linestart')
        endpos = self.textwidget.index('insert lineend')
        text = self.__linetxt(startpos, endpos)
        self.__clearlntags(currln=startpos)
        self.__settags(text, startpos=startpos, endpos=endpos)

    def __settags(self, text, startpos, endpos):
        i = 1
        curpos = startpos
        self.checker.set_text(text)
        for err in self.checker:
            currln = self.textwidget.index('insert linestart')
            tag = '{0}-{1}.{2}'.format(err.word, currln, i)
            mrk = 'mrk-{0}'.format(tag)
            firstltr = self.textwidget.search(err.word, curpos, endpos)
            lastltr = firstltr + ('+%dchars' % len(err.word))

            self.textwidget.tag_config(tag, foreground="red", underline=True)
            self.textwidget.tag_add(tag, firstltr, lastltr)
            self.textwidget.mark_set(mrk, firstltr)
            self.textwidget.tag_bind(tag, '<Button-3>', lambda event,
                                     tag=tag: self.__suggestedwords(event, tag))
            i += 1
            curpos = last_ltr
            self.spellerrs[tag] = (err.word, mrk, currln)

    def __suggestedwords(self, event, tag):
        err = self.spellerrs[tag][0]
        suggwords = self.__suggest(err)
        context_menu = self.__contextmenu(tag, suggwords)
        context_menu.tk_popup(event.x_root, event.y_root)

    def __clearalltags(self):
        if self.spellerrs:
            for tag in self.spellerrs.keys():
                self.__unsettag(self, tag)
            self.spellerrs = {}  # Reset the dictionary

    def __clearlntags(self, currln):
        for tag, val in self.spellerrs.items():
            if val[2] == currln:
                self.__unsettag(self, tag)
                del self.spellerrs[tag]

    def __unsettag(self, tag):
        mrk = self.spellerrs[tag][1]
        self.textwidget.tag_delete(tag)
        self.textwidget.mark_unset(mrk)

    def __alltxt(self):
        return self.textwidget.get(1.0, END)

    def __linetxt(self, startpos, endpos):
        return self.textwidget.get(startpos, endpos)

    def __suggest(self, err):
        return self.suggwords.suggest(err)

    def __contextmenu(self, tag, suggested):
        err = self.spellerrs[tag][0]
        contextmenu = Menu(self.textwidget, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda tag=tag,
                                    word=word: self.__replace(tag, word))
        contextmenu.add_separator()
        contextmenu.add_command(label='Add to Dictionary', command=lambda
                                err=err: self.__usrdict(err))
        return contextmenu

    def __replace(self, tag, word):
        mrk = self.spellerrs[tag][1]
        err = self.spellerrs[tag][0]
        firstltr = self.textwidget.index(mrk)
        lastltr = firstltr + ('+%dchars' % len(err))
        self.textwidget.delete(firstltr, lastltr)
        self.textwidget.insert(firstltr, word)
        self.textwidget.tag_delete(tag)
        self.textwidget.mark_unset(mrk)
        del self.spellerrs[tag]

    def __usrdict(self, err):
        '''TODO: Add a personal dictionary file '''
        pass

if __name__ == '__main__':
    main()
