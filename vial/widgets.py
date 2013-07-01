from . import vim, loop
from .utils import get_key_code, get_winbuf, echo, redraw

class ListFormatter(object):
    def __init__(self, *args):
        self.columns = []
        self.spacing = '  '

        it = iter(args)
        for r in it:
            self.columns.append((r, next(it)))

        self.reset()

    def is_width_changed(self, items, winwidth):
        widths = [0] * len(self.columns)
        rest = winwidth - (len(self.columns) - 1) * len(self.spacing)
        for i, (fn, w) in enumerate(self.columns):
            if w == 0:
                widths[i] = max(self.widths[i], max(len(r[fn]) for r in items))
                rest -= widths[i]
            else:
                widths[i] = w
                if w > 1:
                    rest -= w

        for i, w in enumerate(widths):
            if w < 1:
                widths[i] = round(rest * w)

        if widths != self.widths:
            self.widths = widths
            return True
        else:
            return False

    def reset(self):
        self.widths = [0] * len(self.columns)
    
    def render(self, items):
        fmt = self.spacing.join('{{{}:<{}}}'.format(f[0], w) for f, w in zip(self.columns, self.widths))

        for r in items:
            yield fmt.format(*r)

class ListView(object):
    def __init__(self, items, formatter):
        self.items = items
        self.formatter = formatter
        self.rendered_items = 0
        self.cursor_visible = False

    def attach(self, buf, win):
        self.buf = buf
        self.win = win

    def set_columns(self, *columns):
        self.columns = columns

    def clear(self):
        self.items[:] = []
        self.rendered_items = 0
        self.formatter.reset()

    def render(self, force=False):
        if not self.items:
            self.show_cursor(False)
            self.buf[0:] = ['No matches']

        if force:
            self.rendered_items = 0

        items = self.items[self.rendered_items:]
        if not items:
            return self.rendered_items

        if self.formatter.is_width_changed(items, self.win.width):
            self.rendered_items = 0
            items = self.items

        self.buf[self.rendered_items:] = list(self.formatter.render(items))
        self.rendered_items = len(self.items)

        if self.rendered_items:
            self.show_cursor()

        return self.rendered_items

    def show_cursor(self, show=True):
        if not show:
            vim.command('setlocal nocursorline')
            self.cursor_visible = False
        elif not self.cursor_visible:
            vim.command('setlocal cursorline')
            self.cursor_visible = True
    

class SearchDialog(object):
    def __init__(self, name, list_view):
        self.name = name
        self.list_view = list_view
        self._prompt = u''

    def show(self, prompt=None):
        win, buf = get_winbuf(self.name)
        if win:
            self.win = win
            self.buf = buf
        else:
            if buf:
                vim.command('silent keepalt botright sbuffer {}'.format(buf.number))
            else:
                vim.command('silent keepalt botright split {}'.format(self.name))
                self.loop = loop.Loop(get_key_code('Plug') + 'l')
                self.loop.on_key('CR', self._exit, True)
                self.loop.on_key('Esc', self._exit)
                self.loop.on_key('Up', self._move_cursor, -1)
                self.loop.on_key('C-K', self._move_cursor, -1)
                self.loop.on_key('C-P', self._move_cursor, -1)
                self.loop.on_key('Down', self._move_cursor, 1)
                self.loop.on_key('C-J', self._move_cursor, 1)
                self.loop.on_key('C-N', self._move_cursor, 1)
                self.loop.on_key('BS', self._prompt_changed, None)
                self.loop.on_printable(self._prompt_changed)

                vim.command('setlocal buftype=nofile noswapfile nonumber colorcolumn=')
                vim.command('noremap <buffer> <silent> <Plug>l :python vial.loop.pop()<CR>')

            self.buf = vim.current.buffer
            self.win = vim.current.window

        vim.command('setlocal nobuflisted')
        self.list_view.attach(self.buf, self.win)

        if prompt is not None:
            self._prompt = prompt

        self._update_status()

        if prompt is not None:
            self.on_prompt_changed(prompt)

    def _exit(self, select=False):
        cursor = self.win.cursor
        if select:
            try:
                item = self.list_view.items[cursor[0] - 1]
            except IndexError:
                return

        vim.command('close')
        redraw()
        echo()
        self.loop.exit()

        if select:
            self.on_select(item, cursor)
        else:
            self.on_cancel()

    def _prompt_changed(self, key):
        if key is None:
            self._prompt = self._prompt[:-1]
        else:
            self._prompt += key

        self._update_status()
        self.on_prompt_changed(self._prompt)

    def _move_cursor(self, dir):
        line, col = self.win.cursor
        line = min(len(self.buf), max(1, line + dir))
        self.win.cursor = line, col
        self._update_status()
        self.loop.refresh()

    def _update_status(self):
        redraw()
        echo(u'>>> {}_'.format(self._prompt))

    def on_exit(self): pass
    def on_cancel(self): pass
    def on_select(self, item, cursor): pass
    def on_prompt_changed(self, prompt): pass

