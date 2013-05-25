import os.path

from time import sleep

from vial import vim
from vial.utils import get_key, get_key_code, redraw, echo, get_winbuf

dialog = None
def quick_open():
    global dialog
    if not dialog:
        dialog = QuickOpen()

    dialog.open()

class QuickOpen(object):
    def open(self):
        win, buf = get_winbuf('__vial_quick_open__')
        if win:
            self.win = win
            self.buf = buf
        else:
            vim.command('botright split __vial_quick_open__')
            if not buf:
                vim.command('setlocal buftype=nofile noswapfile cursorline nonumber nobuflisted')
                vim.command('noremap <buffer> <silent> loop :python vial.plugins.quick_open.plugin.dialog.loop()<CR>')

            self.buf = vim.current.buffer
            self.win = vim.current.window

        self.roots = [os.getcwd()]
        self.filelist = []
        self.fill_with_dirs()

        self.prompt = u''
        self.update_status()
        self.loop()

    def loop(self):
        while True:
            key, is_special = get_key()
            if key:
                if is_special:
                    if key == get_key_code('CR') or key == get_key_code('ESC'):
                        break

                    elif key == get_key_code('Down'):
                        line, col = self.win.cursor
                        if line < len(self.buf):
                            line += 1
                        self.win.cursor = line, col
                    elif key == get_key_code('Up'):
                        line, col = self.win.cursor
                        if line > 1:
                            line -= 1
                        self.win.cursor = line, col

                    elif key == get_key_code('BS'):
                        self.prompt = self.prompt[:-1]
                else:
                    self.prompt += key

                self.update_status()
            else:
                sleep(0.02)
                vim.func.feedkeys('loop')
                return

        vim.command('close')
        redraw()
        echo()

    def update_status(self):
        redraw()
        echo(u'>>> {}_'.format(self.prompt))

    def fill_with_dirs(self, root='', top='', place=False):
        dirs = []
        files = []

        # conf = self.pwindow().manager.conf
        hidden_masks = None
        # if not conf['QUICK_OPEN_SHOW_HIDDEN']:
        #     hidden_masks = conf['QUICK_OPEN_HIDDEN_FILES']

        if not top and len(self.roots) > 1:
            for r in self.roots:
                dirs.append((os.path.basename(r), r, os.path.dirname(r), ''))
        else:
            if not top:
                root = self.roots[0]

            for name in os.listdir(os.path.join(root, top)):
                if hidden_masks and any(name.endswith(m) for m in hidden_masks):
                    continue

                fpath = os.path.join(root, top, name)
                if os.path.isdir(fpath):
                    dirs.append((name + '/', fpath, root, top))
                else:
                    files.append((name, fpath, root, top))

        self.filelist[:] = []
        place_idx = 0
        for i, (name, fpath, root, top) in enumerate(sorted(dirs) + sorted(files)):
            if name == place:
                place_idx = i
            self.filelist.append((name, top, fpath, root))

        self.render_filelist(0, place_idx)
        # if place and len(self.filelist):
        #     self.filelist_tree.set_cursor((place_idx,))
        
    def render_filelist(self, start, cursor):
        for i, (name, top, _, _) in enumerate(self.filelist[start:], start):
            self.buf[i:] = ['  ' + name]
