import tk
from tkspellcheck import TextEventMixin, Spellcheck
from exampletext import ykanttoriread

class ExampleUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.topframe = tk.Frame(self)
        self.topframe.pack(side=tk.TOP, fill=tk.X)
        self.status = tk.Label(self.topframe, width=15, relief=tk.SUNKEN)
        self.status.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.cstatus = tk.Label(self.topframe, width=15, relief=tk.SUNKEN)
        self.cstatus.pack(side=tk.RIGHT, fill=tk.X)

        clear = tk.Button(self.topframe, text='Clear Display',
                       command=self.cleardisplay)
        clear.pack(side=tk.RIGHT, fill=tk.X)
        on = tk.Button(self.topframe, text='Spellcheck On',
                    command=self.spellcheck_on)
        on.pack(side=tk.RIGHT, fill=tk.X)
        off = tk.Button(self.topframe, text='Spellcheck Off',
                     command=self.spellcheck_off)
        off.pack(side=tk.RIGHT, fill=tk.X)

        self.text = ExampleText(self, width=80, wrap=tk.WORD)
        self.text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        if self.text.spellcheck.spellcheck_enabled:
            self.cstatus.config(text='Spellcheck is on')
        elif not self.text.spellcheck.spellcheck_enabled:
            self.cstatus.config(text='Spellcheck is off')

        self.text.insert('end', ykanttoriread)
        self.text.spellcheck.reload()

    def spellcheck_on(self):
        self.text.spellcheck.enable_spellcheck()
        self.cstatus.config(text='Spellcheck is on')

    def spellcheck_off(self):
        self.text.spellcheck.disable_spellcheck()
        self.cstatus.config(text='Spellcheck is off')

    def cleardisplay(self):
        self.text.delete('1.0', 'end')

    def update_wordcount(self):
        wc = len(self.text.get('1.0', 'end').split(' '))
        wcount = 'Wordcount: {0}'.format(wc)
        self.status.config(text=wcount)

class ExampleText(TextEventMixin, tk.ScrolledText):
    """Adapted from: http://code.activestate.com/recipes/464635
    """
    def __init__(self, root, *args, **kw):
        tk.ScrolledText.__init__(self, root, *args, **kw)
        self.root = root
        self.spellcheck = Spellcheck(self)
        self.spellcheck.spellcheck_enabled = True
        self._init_textevent_mixin()

    def fire_on_textevent(self):
        self.root.update_wordcount()
        self.spellcheck.run()

def main():
    app = ExampleUI()
    app.mainloop()

if __name__ == '__main__':
    main()
