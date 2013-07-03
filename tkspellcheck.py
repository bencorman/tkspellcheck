from Tkinter import *
import enchant
from enchant.checker import SpellChecker


class tkSpellCheck(Text):
    def __init__(self, master=None, cnf={}, **kw):
        Text.__init__(self, master, cnf, **kw)

    def enable_inline_spellcheck(self, lang='en_US', usrdict=[]):
        self.suggwords = enchant.Dict(lang)
        self.checker = SpellChecker(lang)
        self.spellingerrors = {}
        self.counter = 0
        self.__initialcheck()

    def full_document_spellcheck(self, lang='en_US', usrdict=[]):
        self.__cleartags()
        text = self.__gettxt()
        self.__settags(text, 1.0, END)

    def disable_inline_spellcheck(self):
        self.__cleartags()
        self.__clearbindings()

    def clear_document(self):
        self.__cleartags()
        self.__clearbindings()      # Just in Case

    def __initialcheck(self):
        text = self.__gettxt()
        self.__settags(text, 1.0, END)
        self.bind('<space>', self.__checkline)
        self.bind('<Key>', self.__checkcorrections)

    def __checkcorrections(self, evt):
        for tag in self.spellingerrors.keys():
            firstltr, lastltr = self.__tagranges(tag)
            text = self.__gettxt(firstltr, lastltr)
            if text != self.spellingerrors[tag][0]:
                self.__deltag(tag)
                self.__settags(text, firstltr, lastltr)

    def __checkline(self, evt):
        print self.counter
        self.__del_existing_tags(INSERT)
        startpos = self.index('insert linestart')
        endpos = self.index('insert lineend')
        text = self.__gettxt(startpos, endpos)
        self.__settags(text, startpos, endpos)

    def __del_existing_tags(self, idx):
        taglist = self.__istagged(idx)
        for tag in taglist:
            if tag in self.spellingerrors.keys():
                self.__deltag(tag)

    def __check_existing_tags(self, idx):
        taglist = self.__istagged(idx)
        for tag in taglist:
            if tag in self.spellingerrors.keys():
                return True
            else:
                return False

    def __settags(self, text, startpos, endpos):
        curpos = startpos
        self.checker.set_text(text)
        for err in self.checker:
            firstltr = self.search(err.word, curpos, endpos)
            lastltr = firstltr + ('+%dchars' % len(err.word))
            found = self.__check_existing_tags(firstltr)
            if not found:
                tag = '{0}-{1}'.format(err.word, self.counter)
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

                self.spellingerrors[tag] = (err.word, markleft, markright,
                                            self.counter)
                self.counter += 1
            curpos = lastltr

    def __istagged(self, idx):
        return self.tag_names(idx)

    def __suggestedwords(self, evt, tag):
        err = self.spellingerrors[tag][0]
        suggwords = self.__suggest(err)
        context_menu = self.__contextmenu(tag, suggwords)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def __cleartags(self):
        for tag in self.spellingerrors.keys():
            self.__deltag(tag)
        self.counter = 0

    def __clearbindings(self):
        self.bind('<space>', lambda e: None)

    def __deltag(self, tag):
        self.tag_delete(tag)
        for i in (self.spellingerrors[tag][1], self.spellingerrors[tag][2]):
            self.mark_unset(i)
        del self.spellingerrors[tag]

    def __gettxt(self, startpos=1.0, endpos=END):
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
