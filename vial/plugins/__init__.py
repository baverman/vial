import sys
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

def init_plugins(manager, names):
    for name in names:
        try:
            p = get_plugin(name)
        except:
            log.exception('Plugin import failed')
        else:
            manager.add_plugin(p)

class Manager(object):
    def __init__(self):
        self.plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)
        try:
            plugin.init()
        except:
            log.exception('Plugin init failed')

