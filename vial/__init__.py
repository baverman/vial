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

from .compat import sstr

python_version = sstr(vim.vars.get('vial_python', 'python'))
pyeval_version = 'py3eval' if python_version == 'python3' else 'pyeval'

from .helpers import (register_command, register_function, VimLoggingHandler,
                      vfunc, ref, dref, refs, lfunc, PluginManager, python)

plugin_manager = None


def init():
    import logging
    root_logger = logging.getLogger()
    root_logger.handlers[:] = []
    root_logger.addHandler(logging.FileHandler('/tmp/vial-error.log'))
    root_logger.addHandler(VimLoggingHandler())

    global plugin_manager
    plugin_manager = PluginManager()

    def reload_plugin(plugin_name):
        plugin_manager.remove(plugin_name)
        plugin_manager.add(plugin_name)

    register_command('VialReloadPlugin', reload_plugin, nargs=1)

    for plugin in vim.vars.get('vial_plugins', []):
        plugin_manager.add(plugin)

    if not vim.vars.get('vial_disable_auto_discovery'):
        plugin_manager.add_from(vim.eval('&runtimepath').split(','))

    init_session()


def init_session():
    if not vim.vvars.get('this_session'):
        return

    vial_session_fname = vim.vvars['this_session']
    if vial_session_fname.endswith('.vim'):
        vial_session_fname = vial_session_fname[:-4]

    vial_session_fname += 'v.vim'
    vim.command('silent! source {}'.format(vfunc.fnameescape(vial_session_fname)))
