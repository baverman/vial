from . import vim, loop, python_version
from .compat import sstr
from .utils import get_key_code, echo, redraw, focus_window, get_buf_by_name, eval_cache


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
        fmt = self.spacing.join('{{{}:<{}}}'.format(f[0], w)
                                for f, w in zip(self.columns, self.widths))

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
    def __init__(self, name, list_view, title=None):
        self.name = name
        self.title = title or name
        self.list_view = list_view
        self._prompt = u''
        self.loop = None

    def init(self, win, buf):
        self.loop = loop.Loop(get_key_code(r'\<Plug>l'))
        self.loop.on_key(r'\<CR>',   self._exit, True)
        self.loop.on_key(r'\<Esc>',  self._exit)
        self.loop.on_key(r'\<C-L>',  self._select)
        self.loop.on_key(r'\<Up>',   self._move_cursor, -1)
        self.loop.on_key(r'\<C-K>',  self._move_cursor, -1)
        self.loop.on_key(r'\<C-P>',  self._move_cursor, -1)
        self.loop.on_key(r'\<Down>', self._move_cursor, 1)
        self.loop.on_key(r'\<C-J>',  self._move_cursor, 1)
        self.loop.on_key(r'\<C-N>',  self._move_cursor, 1)
        self.loop.on_key(r'\<BS>',   self._prompt_changed, None)
        self.loop.on_printable(self._prompt_changed)
        vim.command('noremap <buffer> <silent> <Plug>l :{} vial.loop.pop()<CR>'.format(python_version))

    def show(self, prompt=None):
        self.win, self.buf = make_scratch(self.name, self.init,
                                          self.title, force=not self.loop)
        self.list_view.attach(self.buf, self.win)

        if prompt is not None:
            self._prompt = prompt

        self._update_status()

        if prompt is not None:
            self.on_prompt_changed(prompt)

    def _select(self):
        cursor = self.win.cursor
        try:
            item = self.list_view.items[cursor[0] - 1]
        except IndexError:
            return

        self.on_select(item, cursor)
        focus_window(self.win.number)
        self._update_status()

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
            self._prompt += sstr(key)

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


def find_scratch_window():
    for w in vim.windows:
        if w.valid and '_vial_scratch' in w.vars:
            return w


def make_scratch(name, init=None, title=None, force=False, placement=None, focus=True):
    cwin = vim.current.window
    win = find_scratch_window()
    ebuf = get_buf_by_name(name)
    if not win:
        placement = placement or 'botright'
        if ebuf:
            vim.command('silent keepalt {} sbuffer {}'.format(placement,
                                                              ebuf.number))
        else:
            vim.command('silent keepalt {} split {}'.format(placement, name))

        win = vim.current.window
        buf = vim.current.buffer
    else:
        focus_window(win)
        if ebuf:
            vim.command('silent keepalt buffer {}'.format(name))
            buf = ebuf
        else:
            vim.command('silent keepalt edit {}'.format(name))
            buf = vim.current.buffer

    win.vars['_vial_scratch'] = 1
    if not ebuf or force:
        vim.command('setlocal buftype=nofile noswapfile nonumber colorcolumn=')
        if title:
            win.options['statusline'] = title
        init and init(win, buf)

    vim.command('setlocal nobuflisted')

    if not focus:
        focus_window(cwin)

    return win, buf
