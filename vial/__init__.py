VERSION = '0.1dev'

try:
    import vim
except ImportError:
    class vim:
        vars = {}
        vvars = {}

if not hasattr(vim, 'vars'):
    vim.vars = vim.bindeval('g:')

if not hasattr(vim, 'vvars'):
    vim.vvars = vim.bindeval('v:')


class VimFuncs(object):
    def __init__(self):
        self._cache = {}

    def __getattr__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            pass

        func = self._cache[name] = vim.bindeval('function("{}")'.format(name))
        return func

vfunc = VimFuncs()
event = None
plugin_manager = None

def init():
    import logging
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    global event, plugin_manager

    event = EventManager()

    import vial.utils
    import vial.plugins

    plugin_manager = vial.plugins.Manager()
    plugin_manager.add_from(vim.eval('&runtimepath').split(','))
    plugin_manager.add('grep')
    plugin_manager.init()

    init_session()

    vim.command('augroup VialFileType')
    vim.command('autocmd!')
    vim.command('autocmd FileType * python vial.filetype_changed()')
    vim.command('augroup END')

    for b in vim.buffers:
        _emit_ft(b, vfunc.getbufvar(b.number, '&filetype'))

def init_session():
    if 'this_session' not in vim.vvars.keys():
        return

    vial_session_fname = vim.vvars['this_session']
    if vial_session_fname.endswith('.vim'):
        vial_session_fname = vial_session_fname[:-4]

    vial_session_fname += 'v.vim'
    vim.command('silent! source {}'.format(vial_session_fname)) # TODO: escape

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


