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

def get_plugin(name):
    package_name = 'vial.plugins.' + name
    return get_package(package_name)

def find_plugins(path):
    plugins = []
    for p in path:
        vp = os.path.join(p, 'vial-plugin')
        if os.path.exists(vp):
            if vp not in __path__:
                __path__.insert(0, vp)

            for name in os.listdir(vp):
                if os.path.exists(os.path.join(vp, name, '__init__.py')):
                    plugins.append(name)
    
    return plugins


class Manager(object):
    def __init__(self):
        self.plugins = []

    def add_from(self, path):
        for name in find_plugins(path):
            try:
                self.add(get_plugin(name))
            except:
                log.exception('Plugin import failed')

    def add(self, plugin):
        self.plugins.append(plugin)

    def init(self):
        for p in self.plugins:
            try:
                p.init()
            except:
                log.exception('Plugin init failed')

