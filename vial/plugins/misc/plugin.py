from vial import vfunc, vim
from vial.utils import buffer_with_file, focus_window, vimfunction, get_ws_len, mark
from vial.widgets import SearchDialog, ListFormatter, ListView

def escape():
    if len(vim.windows) < 2:
        return

    cur = vfunc.winnr()
    
    for n, w in reversed(list(enumerate(vim.windows, 1))):
        if not buffer_with_file(w.buffer):
            focus_window(n)
            vim.command('q')
            if n != cur:
                if cur > n:
                    cur -= 1

                focus_window(cur)

            return

def shift_indent(line, shift=1):
    return vfunc.indent(line-1) + shift * vfunc.eval('&sw')

@vimfunction
def indent():
    line = vim.current.window.cursor[0]
    buf = vim.current.buffer
    if buf[line-2].endswith(':'):
        return shift_indent(line)

    cline = buf[line-1].lstrip() 
    if cline and cline[0] in [')', ']', '}']:
        pline = buf[line-2].rstrip() 
        if pline and pline[-1] in ['(', '[', '{']:
            return shift_indent(line)

    return -1

search_outline_dialog = None
def search_outline():
    global search_outline_dialog
    if not search_outline_dialog:
        search_outline_dialog = SearchOutlineDialog()

    search_outline_dialog.open()

class SearchOutlineDialog(SearchDialog):
    def __init__(self):
        self.lines = []
        SearchDialog.__init__(self, '__vial_search_outline__', 
            ListView(self.lines, ListFormatter(2,0, 3,1)))

    def open(self):
        self.last_window = vfunc.winnr()
        self.sbuf = vim.current.buffer
        self.list_view.clear()
        self.show(u'')
        self.loop.enter()

    def on_select(self, item, cursor):
        focus_window(self.last_window)
        mark()
        vim.command('normal! {}Gzz^'.format(item[1]))

    def on_cancel(self):
        focus_window(self.last_window)

    def on_prompt_changed(self, prompt):
        if prompt:
            self.fill(prompt.encode('utf-8'))
        else:
            self.list_view.show_cursor(False)
            self.buf[0:] = ['Type something to search']
            self.loop.refresh()

    def fill(self, prompt):
        current = self.current = object()
        self.list_view.clear()

        for i, line in enumerate(self.sbuf, 1):
            if current is not self.current:
                return

            if prompt in line:
                self.lines.append((get_ws_len(line), i, str(i), line))

        self.lines.sort()
        self.list_view.render()
        self.loop.refresh()
