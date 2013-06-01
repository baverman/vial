import vial

from . import vim
from .plugins import Manager as PluginManager
from .utils import get_buf

class Manager(object):
    def __init__(self):
        self.callbacks = {}

    def init(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.add_from(vim.eval('&runtimepath').split(','))
        self.plugin_manager.init()

        vim.command('augroup VialFileType')
        vim.command('autocmd!')
        vim.command('autocmd FileType * python vial.manager.filetype_changed()')
        vim.command('augroup END')

        for b in vim.buffers:
            self._emit_ft(b, vial.vfunc.getbufvar(b.number, '&filetype'))
            
    def emit(self, name, *args):
        if name in self.callbacks:
            for c in self.callbacks[name]:
                c(*args)

    def on(self, name, callback):
        self.callbacks.setdefault(name, []).append(callback)

    def register_command(self, name, callback):
        setattr(vial, name, callback)
        vim.command('''command! -nargs=0 {0} :python vial.{0}()'''.format(name))

    def filetype_changed(self):
        ft = vial.vfunc.expand('<amatch>')
        bufnr = int(vial.vfunc.expand('<abuf>'))
        buf = get_buf(bufnr)
        self._emit_ft(buf, ft)

    def _emit_ft(self, buf, ft):
        self.emit('filetype', buf, ft)
        for r in ft.split('.'):
            self.emit('filetype:{}'.format(r), buf)
