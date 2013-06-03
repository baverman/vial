VERSION = '0.1dev'

try:
    import vim
except ImportError:
    class vim:
        pass

event = None
plugin_manager = None

from . import utils
from . import plugins

def init():
    import logging
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    global event, plugin_manager

    event = EventManager()

    plugin_manager = plugins.Manager()
    plugin_manager.add_from(vim.eval('&runtimepath').split(','))
    plugin_manager.init()

    vim.command('augroup VialFileType')
    vim.command('autocmd!')
    vim.command('autocmd FileType * python vial.filetype_changed()')
    vim.command('augroup END')

    for b in vim.buffers:
        _emit_ft(b, vfunc.getbufvar(b.number, '&filetype'))

def event_received():
    event = vim.eval("a:event")
    # print(event)

def register_command(name, callback, **opts):
    globals()[name] = callback
    fargs = '' if opts.get('nargs', 0) < 1 else '<f-args>'
    opts = ' '.join('-{}={}'.format(*r) for r in opts.iteritems())
    vim.command('''command! {1} {0} python vial.{0}({2})'''.format(name, opts, fargs))

def register_function(signature, callback):
    name = signature.partition('(')[0]
    globals()[name] = callback
    vim.command('''function! {0}
      python vial.{1}()
      return a:result
    endfunction'''.format(signature, name))

def filetype_changed():
    ft = vfunc.expand('<amatch>')
    bufnr = int(vfunc.expand('<abuf>'))
    buf = utils.get_buf(bufnr)
    _emit_ft(buf, ft)

def _emit_ft(buf, ft):
    event.emit('filetype', buf, ft)
    for r in ft.split('.'):
        event.emit('filetype:{}'.format(r), buf)

class EventManager(object):
    def __init__(self):
        self.callbacks = {}

    def emit(self, name, *args):
        if name in self.callbacks:
            for c in self.callbacks[name]:
                c(*args)

    def on(self, name, callback):
        self.callbacks.setdefault(name, []).append(callback)
