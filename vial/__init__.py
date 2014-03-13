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
plugin_manager = None
refs = {}


def init():
    import logging
    import vial.utils
    root_logger = logging.getLogger()
    root_logger.handlers[:] = []
    root_logger.addHandler(utils.VimLoggingHandler())

    import vial.plugins
    global plugin_manager
    plugin_manager = vial.plugins.Manager()
    plugin_manager.add_from(vim.eval('&runtimepath').split(','))
    plugin_manager.add('vial.plugins.grep')
    plugin_manager.add('vial.plugins.misc')
    plugin_manager.add('vial.plugins.bufhist')
    plugin_manager.init()

    init_session()


def init_session():
    if 'this_session' not in vim.vvars.keys():
        return

    vial_session_fname = vim.vvars['this_session']
    if vial_session_fname.endswith('.vim'):
        vial_session_fname = vial_session_fname[:-4]

    vial_session_fname += 'v.vim'
    vim.command('silent! source {}'.format(vfunc.fnameescape(vial_session_fname)))


def register_command(name, callback, **opts):
    fargs = '' if opts.get('nargs', 0) < 1 else '<f-args>'
    opts = ' '.join('-{}={}'.format(*r) for r in opts.iteritems())
    vim.command('''command! {1} {0} python {2}({3})'''.format(
        name, opts, ref(callback, 1), fargs))


def register_function(signature, callback):
    vim.command('''function! {0}
      python {1}()
      return a:result
    endfunction'''.format(signature, ref(callback, 1)))


class ref(object):
    def __init__(self, fn, depth=0):
        if isinstance(fn, basestring):
            fn = utils.lfunc(fn, depth + 1)

        ofn = fn

        fn = getattr(fn, 'func', fn)
        if hasattr(fn, 'is_lazy'):
            line = 'lazy'
        else:
            line = fn.__code__.co_firstlineno

        name = '{}.{}:{}'.format(
            fn.__module__, fn.__name__, line)

        self.name = name
        refs[name] = ofn

    def __call__(self, *args, **kwargs):
        return refs[self.name](*args, **kwargs)

    def __str__(self):
        return "vial.refs['{}']".format(self.name)


def dref(func):
    func.ref = ref(func)
    return func
