import sys
import os.path
import logging

log = logging.getLogger(__name__)


def get_package(name):
    try:
        return sys.modules[name]
    except KeyError:
        __import__(name)
        return sys.modules[name]


def find_plugins(path):
    plugins = []
    pypath = []
    for p in path:
        vp = os.path.join(p, 'vial-plugin')
        if os.path.exists(vp):
            pypath.append(vp)
            for name in os.listdir(vp):
                if name.endswith('.py'):
                    plugins.append(name[:-3])
                elif os.path.exists(os.path.join(vp, name, '__init__.py')):
                    plugins.append(name)

    return plugins, pypath


class Manager(object):
    def __init__(self):
        self.plugins = []

    def add_from(self, path):
        plugins, pypath = find_plugins(path)
        sys.path.extend(pypath)
        for name in plugins:
            self.add(name)

    def add(self, name):
        try:
            self._add(get_package(name))
        except:
            log.exception('Plugin import failed: %s', name)

    def _add(self, plugin):
        self.plugins.append(plugin)

    def init(self):
        for p in self.plugins:
            if hasattr(p, 'init'):
                try:
                    p.init()
                except:
                    log.exception('Plugin init failed: %s', p.__name__)
