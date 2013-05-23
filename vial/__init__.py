VERSION = '0.1dev'

try:
    import vim
except ImportError:
    class vim:
        pass

manager = None

from . import utils

def init():
    import logging
    from .manager import Manager

    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    global manager
    manager = Manager()
    manager.init()

# def filetype_changed():
#     bufn = expand('<abuf>')
#     filetype = expand('<amatch>')

def event_received():
    event = vim.eval("a:event")
    # print(event)

