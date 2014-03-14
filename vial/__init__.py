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

from .helpers import register_command, register_function, VimLoggingHandler, \
    vfunc, ref, dref, refs, lfunc

plugin_manager = None


def init():
    import logging
    root_logger = logging.getLogger()
    root_logger.handlers[:] = []
    root_logger.addHandler(VimLoggingHandler())

    import vial.plugins
    global plugin_manager
    plugin_manager = vial.plugins.Manager()
    plugin_manager.add_from(vim.eval('&runtimepath').split(','))
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
