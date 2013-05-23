import vial

from . import vim
from .plugins import Manager as PluginManager, init_plugins

class Manager(object):
    def __init__(self):
        self.callbacks = {}

    def var(self, name, default=None):
        try:
            return vim.vars[name]
        except KeyError:
            return default

    def init(self):
        self.plugin_manager = PluginManager()
        init_plugins(self.plugin_manager, self.var('vial_plugins', []))

    def emit(self, name, *args):
        if name in self.callbacks:
            for c in self.callbacks[name]:
                c(*args)

    def on(self, name, callback):
        self.callbacks.setdefault(name, []).append(callback)

    def register_command(self, name, callback):
        setattr(vial, name, callback)
        vim.command('''command! -nargs=0 {0} :python vial.{0}()'''.format(name))

