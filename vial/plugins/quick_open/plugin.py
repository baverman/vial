import os.path
import re

from time import sleep

from vial import vim
from vial.utils import get_key, get_key_code, redraw, echo, get_winbuf
from vial.events import Loop

from .. import quick_open as module
from . import search

module.dialog = None

IGNORE_DIRS = re.compile(r'(^|.*/)(\.git|\.svn|\.hg)$')
IGNORE_FILES = re.compile(r'^.*(\.pyc|\.pyo|\.swp|\.class|\.o)$')

def quick_open():
    if not module.dialog:
        module.dialog = QuickOpen()

    module.dialog.open()

class QuickOpen(object):
    def __init__(self):
        self.prompt = u''
        self.filelist = []

    def open(self):
        win, buf = get_winbuf('__vial_quick_open__')
        if win:
            self.win = win
            self.buf = buf
        else:
            vim.command('botright split __vial_quick_open__')
            if not buf:
                self.loop = Loop(get_key_code('Plug') + 'l')
                self.loop.on_key('CR', self.exit, True)
                self.loop.on_key('Esc', self.exit)
                self.loop.on_key('Up', self.move_cursor, -1)
                self.loop.on_key('Down', self.move_cursor, 1)
                self.loop.on_key('BS', self.prompt_changed, None)
                self.loop.on_printable(self.prompt_changed)

                vim.command('setlocal buftype=nofile noswapfile cursorline nonumber')
                vim.command('noremap <buffer> <silent> <Plug>l '
                    ':python vial.plugins.quick_open.dialog.loop.enter()<CR>')

            self.buf = vim.current.buffer
            self.win = vim.current.window

        vim.command('setlocal nobuflisted')
        self.roots = [os.getcwd()]

        self.prompt = u''
        self.update_status()
        self.loop.enter()

    def exit(self, select=False):
        cursor = self.win.cursor
        vim.command('close')
        if select:
            try:
                fname = self.filelist[cursor[0] - 1][2]
                vim.command('e {}'.format(fname))
            except IndexError:
                pass

        redraw()
        echo()
        self.loop.exit()

    def move_cursor(self, dir):
        line, col = self.win.cursor
        line += dir

        if line < 1:
            line = 1

        if line > len(self.buf):
            line = len(self.buf)

        self.win.cursor = line, col
        self.loop.refresh()

    def prompt_changed(self, key):
        if key is None:
            self.prompt = self.prompt[:-1]
        else:
            self.prompt += key

        self.update_status()
        if self.prompt:
            self.loop.idle(self.fill())

    def update_status(self):
        if not self.prompt:
            self.buf[0:] = ['Type something to search']

        redraw()
        echo(u'>>> {}_'.format(self.prompt))

    def fill(self):
        current = self.current = object()
        self.filelist[:] = []
        last_index = 0
        cnt = 0
        already_matched = {}

        for m in search.get_matchers(self.prompt):
            for r in self.roots:
                for name, path, root, top, fpath in search.get_files(r, '', IGNORE_FILES, IGNORE_DIRS):
                    if current is not self.current:
                        return

                    if fpath not in already_matched and m(name, path):
                        already_matched[fpath] = True
                        self.filelist.append((name, top, fpath, root))

                    cnt += 1
                    if not cnt % 50:
                        last_index = self.render(last_index)
                        if last_index > 20:
                            self.loop.refresh()
                            return

                        yield
                        
        if not self.render(last_index):
            self.buf[0:] = ['Matches not found']

        self.loop.refresh()

    def render(self, start):
        if start < len(self.filelist):
            for i, (name, top, _, _) in enumerate(self.filelist[start:], start):
                self.buf[i:] = ['  {}  {}'.format(name, top)]

        return len(self.filelist)
