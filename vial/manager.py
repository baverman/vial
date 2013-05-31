import vial

from . import vim
from .plugins import Manager as PluginManager

class Manager(object):
    def __init__(self):
        self.callbacks = {}

    def init(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.add_from(vim.eval('&runtimepath').split(','))
        self.plugin_manager.init()

    def emit(self, name, *args):
        if name in self.callbacks:
            for c in self.callbacks[name]:
                c(*args)

    def on(self, name, callback):
        self.callbacks.setdefault(name, []).append(callback)

    def register_command(self, name, callback):
        setattr(vial, name, callback)
        vim.command('''command! -nargs=0 {0} :python vial.{0}()'''.format(name))

