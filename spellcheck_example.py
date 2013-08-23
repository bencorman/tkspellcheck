from Tkinter import *
from ttk import *
from tkspellcheck import ModifiedText
from exampletext import ykanttoriread

class ExampleUI(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.topframe = Frame(self)
        self.topframe.pack(side=TOP, fill=X)
        self.status = Label(self.topframe)
        self.status.pack(side=RIGHT, fill=X, expand=1, anchor=W)
        self.cstatus = Label(self.topframe, width=25)
        self.cstatus.pack(side=RIGHT, fill=X)

        clear = Button(self.topframe, text='Clear Display',
                       command=self.cleardisplay)
        clear.pack(side=RIGHT, fill=X)
        on = Button(self.topframe, text='Spellcheck On',
                    command=self.spellcheck_on)
        on.pack(side=RIGHT, fill=X)
        off = Button(self.topframe, text='Spellcheck Off',
                     command=self.spellcheck_off)
        off.pack(side=RIGHT, fill=X)

        self.text = ExampleText(self, width=80, wrap=WORD)
        self.text.pack(side=BOTTOM, fill=BOTH, expand=1)

        if self.text.spellcheck_enabled:
            self.status.config(text='Spellcheck is on')
        elif not self.text.spellcheck_enabled:
            self.status.config(text='Spellcheck is off')

        self.text.insert('end', ykanttoriread)
        self.text.reload()

    def spellcheck_on(self):
        self.text.enable_spellcheck()
        self.status.config(text='Spellcheck is on')

    def spellcheck_off(self):
        self.text.disable_spellcheck()
        self.status.config(text='Spellcheck is off')

    def cleardisplay(self):
        self.text.delete('1.0', 'end')

class ExampleText(ModifiedText):
    def __init__(self, master, *args, **kwargs):
        ModifiedText.__init__(self, master, *args, **kwargs)
        self.master = master

    def fire_on_textevent(self):
        wc = len(self.get('1.0', 'end').split(' '))
        self.master.cstatus.config(text='Total Words: {0}'.format(wc))
        self.fire_spellcheck()

def main():
    app = ExampleUI()
    app.mainloop()

if __name__ == '__main__':
    main()
