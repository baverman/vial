import sys
import os.path
import logging
import weakref

log = logging.getLogger(__name__)

def get_package(name):
    try:
        return sys.modules[name]
    except KeyError:
        __import__(name)
        return sys.modules[name]

def find_plugins(path):
    plugins = []
    for p in path:
        vp = os.path.join(p, 'vial-plugin')
        if os.path.exists(vp):
            if vp not in __path__:
                __path__.insert(0, vp)

            for name in os.listdir(vp):
                if os.path.exists(os.path.join(vp, name, '__init__.py')):
                    plugins.append('vial.plugins.' + name)
    
    return plugins


class Manager(object):
    def __init__(self):
        self.plugins = []

    def add_from(self, path):
        for name in find_plugins(path):
            self.add(name)

    def add(self, name):
        try:
            self._add(get_package(name))
        except:
            log.exception('Plugin import failed')

    def _add(self, plugin):
        self.plugins.append(plugin)

    def init(self):
        for p in self.plugins:
            try:
                p.init()
            except:
                log.exception('Plugin init failed')

