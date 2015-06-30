import re
import os.path
import fnmatch

from subprocess import Popen, PIPE

from vial import vfunc, vim
from vial.utils import (buffer_with_file, focus_window, get_ws_len, mark,
                        echo, get_projects, get_dvar)
from vial.widgets import SearchDialog, ListFormatter, ListView


def escape():
    if len(vim.windows) < 2:
        return

    cur = vfunc.winnr()

    for n, w in reversed(list(enumerate(vim.windows, 1))):
        if not buffer_with_file(w.buffer):
            if not '[Command Line]'in w.buffer.name:
                focus_window(n)
            vim.command('q')
            if n != cur:
                if cur > n:
                    cur -= 1

                focus_window(cur)

            return


def shift_indent(line, shift=1):
    return vfunc.indent(line-1) + shift * vfunc.eval('&sw')


parens = {'(': ')', '{': '}', '[': ']'}
rparens = {v: k for k, v in parens.iteritems()}
pescape = {'(': '(', ')': ')', '[': '\[', ']': '\]', '{': '{', '}': '}'}


def indent():
    line, pos = vim.current.window.cursor
    buf = vim.current.buffer
    if buf[line-2].endswith(':'):
        return shift_indent(line)

    pline = buf[line-2].rstrip()
    if pline and pline[-1] in parens.keys():
        return shift_indent(line)

    if pline:
        start, closeb = max((pline.rfind(b), b) for b in parens.values())
        if start >= 0:
            openb = rparens[closeb]
            vfunc.cursor(line - 1, start + 1)
            l, _ = vfunc.searchpairpos(pescape[openb], '', pescape[closeb],
                                       'nWb', '', max(0, line - 30))
            if l and l != line - 1:
                return vfunc.indent(l)

        start = -1
        while True:
            start, openb = max((pline.rfind(b, 0, start), b)
                               for b in parens.keys())
            if start < 0: break
            vfunc.cursor(line - 1, start + 1)
            l, _ = vfunc.searchpairpos(pescape[openb], '',
                                       pescape[parens[openb]], 'nW', '', line)
            if not l or l != line - 1:
                return start + 1

    w = vfunc.indent(line-1)
    if not buf[line-1].strip() and w != pos:
        return -1

    return w


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
                              ListView(self.lines, ListFormatter(2, 0, 3, 1)))

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
            self.fill(prompt)
        else:
            self.list_view.show_cursor(False)
            self.buf[0:] = ['Type something to search']
            self.loop.refresh()

    def fill(self, prompt):
        current = self.current = object()
        self.list_view.clear()

        ignorecase = prompt == prompt.lower()
        if ignorecase:
            prompt = prompt.lower()

        for i, line in enumerate(self.sbuf, 1):
            if current is not self.current:
                return

            l = line.decode('utf-8')
            if ignorecase:
                l = l.lower()

            if prompt in l:
                self.lines.append((get_ws_len(line), i, str(i), line))

        self.lines.sort()
        self.list_view.render()
        self.loop.refresh()


def changed_projects():
    changed = []
    for p in get_projects():
        if not os.path.exists(os.path.join(p, '.git')):
            continue

        proc = Popen(['git', 'status', '-b', '--porcelain'],
                     cwd=p, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        if proc.returncode != 0:
            if err.strip():
                print err
            else:
                print 'Git error', proc.returncode
        else:
            for line in out.splitlines():
                if not line.startswith('##') or 'ahead' in line:
                    changed.append(p)
                    break

    if changed:
        print ', '.join(os.path.basename(r) for r in changed)
    else:
        echo('There are no any changes')


def new(fname):
    dname = os.path.dirname(fname)
    if not os.path.exists(dname):
        os.makedirs(dname)

    vim.command('e {}'.format(fname))


def filter_qf(pattern):
    qf = vfunc.getqflist()
    if not qf:
        return

    regex = re.compile(fnmatch.translate(pattern))

    result = []
    for r in qf:
        fname = vfunc.bufname(r['bufnr'])
        if regex.match(fname):
            nr = dict(r)
            nr['filename'] = fname
            result.append(nr)

    vfunc.setqflist(result)


def add_projects(bang, *dirs):
    if bang:
        result = []
    else:
        result = list(vim.vars.get('vial_projects', []))
    result.extend(os.path.realpath(os.path.abspath(r)) for r in dirs)
    vim.vars['vial_projects'] = result


def add_ignore_extensions(bang, *exts):
    if bang:
        result = []
    else:
        result = list(get_dvar('vial_ignore_extensions'))
    result.extend(exts)
    vim.vars['vial_ignore_extensions'] = list(set(result))


def add_ignore_dirs(bang, *dirs):
    if bang:
        result = []
    else:
        result = list(get_dvar('vial_ignore_dirs'))
    result.extend(dirs)
    vim.vars['vial_ignore_dirs'] = list(set(result))
