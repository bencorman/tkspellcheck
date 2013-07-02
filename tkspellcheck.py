from Tkinter import *
from ttk import *
import enchant
from enchant.checker import SpellChecker


class tkSpellCheck:
    def __init__(self, textwidget, lang='en_US'):
        self.textwidget = textwidget
        self.swords = enchant.Dict(lang)        # S(uggested) Words, obviously
        self.checker = SpellChecker(lang)
        self.sp_err = {}

    def __call__(self, mode=False):
        if mode == 'init':
            self.fullcheck()
        if mode == 'inline':
            self.inlinecheck()
        if not mode:
            self.destroy_tags()

    def destroy_tags(self):
        if self.sp_err:
            for tag in self.sp_err.keys():
                mrk = self.sp_err[tag][1]
                self.textwidget.tag_delete(tag)
                self.textwidget.mark_unset(mrk)
            self.sp_err = {}  # Reset the dictionary for next time

    def fullcheck(self):
        self.destroy_tags()
        text = self.__alltxt()
        self.checker.set_text(text)
        i = 1
        curpos = 1.0

        for err in self.checker:
            tag = '{0}-{1}'.format(err.word, i)
            mrk = 'mrk-{0}'.format(tag)
            first_ltr = self.textwidget.search(err.word, curpos, END)
            last_ltr = first_ltr + ('+%dchars' % len(err.word))

            self.textwidget.tag_config(tag, foreground="red", underline=True)
            self.textwidget.tag_add(tag, first_ltr, last_ltr)
            self.textwidget.mark_set(mrk, first_ltr)
            self.textwidget.tag_bind(tag, '<Button-3>', lambda event,
                                     tag=tag: self.show_suggestions(event, tag))
            i += 1
            curpos = last_ltr
            self.sp_err[tag] = (err.word, mrk)

    def show_suggestions(self, event, tag):
        err = self.sp_err[tag][0]
        suggested_words = self.__suggest(err)
        context_menu = self.__build_cnxtmnu(tag, suggested_words)
        print event.x_root, event.y_root
        context_menu.tk_popup(event.x_root, event.y_root)

    def __alltxt(self):
        return self.textwidget.get(1.0, END)

    def __suggest(self, err):
        return self.swords.suggest(err)

    def __build_cnxtmnu(self, tag, suggested):
        err = self.sp_err[tag][0]
        cnxtmnu = Menu(self.textwidget, tearoff=False)
        for word in suggested:
            cnxtmnu.add_command(label=word, command=lambda tag=tag,
                                  word=word: self.__replace(tag,word))
        cnxtmnu.add_separator()
        cnxtmnu.add_command(label='Add to Dictionary', command=lambda
                            err=err: self.__usr_def(err))
        return cnxtmnu

    def __replace(self, tag, word):
        mrk = self.sp_err[tag][1]
        err = self.sp_err[tag][0]
        first_ltr = self.textwidget.index(mrk)
        last_ltr = first_ltr + ('+%dchars' % len(err))
        self.textwidget.delete(first_ltr, last_ltr)
        self.textwidget.insert(first_ltr, word)
        self.textwidget.tag_delete(tag)
        self.textwidget.mark_unset(mrk)

    def __usr_def(self, err):
        '''TODO: Add a personal dictionary file '''
        pass

if __name__ == '__main__':
    main()
