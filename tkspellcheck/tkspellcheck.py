import tk
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter, HTMLChunker

class TextEventMixin(object):
    """Adds a trigger to the Tkinter Text widget that fires on modification.

    From: http://code.activestate.com/recipes/464635
    """

    def _init_textevent_mixin(self):
        """Call this from the text widget to bind the <<Modified>> event to the
        Callback.
        """
        # Clear the alert flag and set up the _reset_alert_flag attribute.
        self._reset_alert_flag()

        # Bind the <<Modified>> virtual event to the internal callback.
        self.bind('<<Modified>>', self._txtevt)

    def _txtevt(self, evt):
        """Calls the user callback and resets the <<Modified>> event.
        """

        # If this is being called recursively as a result of the call to
        # _reset_alert_flag() below, then we do nothing.
        if not self._resetting_alert_flag:

            # Clear the Tk 'modified' variable.
            self._reset_alert_flag()

             # Call the user-defined callback.
            self.fire_on_textevent()

    def fire_on_textevent(self):
        """Override this method in your class. This is called whenever the
        <<Modified>> event is triggered.
        """
        pass

    def _reset_alert_flag(self):
        """Reset the <<Modified>> event to false so it'll fire again on the next
        modification.

        Setting the Text Widget's modified variable triggers the <<Modified>>
        event which can trigger _txtevt() recursively.

        This uses the _resetting_alert_flag to disable the internal callback
        _txtevt() to avoid this recursive call.
        """

        # Set the flag, disable the internal callback
        self._resetting_alert_flag = True

        # edit_modified() only recently became a valid call?
        # The Tkinter Text modified variable can also be set via:
        # self.tk.call(self._w, 'edit', 'modified', 0)
        # edit_modified() information here:
        # http://epydoc.sourceforge.net/stdlib/Tkinter.Text-class.html#edit_modified
        self.edit_modified(False)

        # Unset the flag, enable the internal callback
        self._resetting_alert_flag = False

class Spellcheck(object):
    def __init__(self, textwidget, **kw):
        lang = kw.pop('language', 'en_US')
        filters = kw.pop('filters', [EmailFilter, URLFilter])
        chunkers = kw.pop('chunkers', (HTMLChunker,))
        self.checker = SpellChecker(lang=lang, filters=filters, chunkers=chunkers)

        self.tw = textwidget
        self.tw.tag_config('sp_err', background="#CCFB5D", underline=False)

    def enable_spellcheck(self):
        self.spellcheck_enabled = True
        self._tag_remove('1.0', 'end')
        ln = int(self.tw.index('end').split('.')[0])
        while ln:
            start = '{0}.0'.format(ln)
            end = '{0}.end'.format(ln)
            self._check_spelling(start, end, ln)
            ln -= 1

    def disable_spellcheck(self):
        self.spellcheck_enabled = False
        self._tag_remove('1.0', 'end')

    def reload(self):
        if self.spellcheck_enabled:
            self.enable_spellcheck()

    def run(self):
        if self.spellcheck_enabled:
            start, end, ln = self._findposition()
            self._tag_remove(start, end)
            self._check_spelling(start, end, ln)

    def _findposition(self):
        start = self.tw.index('insert linestart')
        end = self.tw.index('insert wordstart')
        ln = int(self.tw.index('insert').split('.')[0])
        return (start, end, ln)

    def _check_spelling(self, start, end, ln):
        self.checker.set_text(self._get_text(start, end))
        for e in self.checker:
            begintag = '{0}.{1}'.format(ln, e.wordpos)
            endtag = begintag + ('+%dchars' % len(e.word))
            self._tag_word(begintag, endtag)

    def _tag_word(self, begintag, endtag):
        self.tw.mark_set('lt-sp_err', begintag)
        self.tw.mark_set('rt-sp_err', endtag)
        self.tw.mark_gravity('lt-sp_err', tk.LEFT)
        self.tw.mark_gravity('rt-sp_err', tk.RIGHT)
        self.tw.tag_add('sp_err', 'lt-sp_err', 'rt-sp_err')
        self.tw.tag_bind('sp_err', '<Button-3>', self._get_suggestions)

    def _get_text(self, start, end):
        return self.tw.get(start, end)

    def _get_suggestions(self, evt):
        self.tw.mark_set('insert', 'current')
        start = self.tw.index('insert wordstart')
        end = self.tw.index('insert wordend')
        suggested = self._suggest(self.tw.get(start, end))
        context_menu = self._generate_contextmenu(start, end, suggested)
        context_menu.tk_popup(evt.x_root, evt.y_root)

    def _suggest(self, e):
        return self.checker.suggest(e)

    def _generate_contextmenu(self, start, end, suggested):
        contextmenu = tk.Menu(self.tw, tearoff=False)
        for word in suggested:
            contextmenu.add_command(label=word, command=lambda start=start,
                                    end=end, word=word: self._replace(start, end, word))
        return contextmenu

    def _replace(self, start, end, word):
        self.tw.delete(start, end)
        self.tw.insert(start, word)
        self._tag_remove(start, end)

    def _tag_remove(self, start, end):
        self.tw.mark_unset('lt-sp_err', start)
        self.tw.mark_unset('rt-sp_err', end)
        self.tw.tag_remove('sp_err', start, end)

