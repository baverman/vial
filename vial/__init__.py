VERSION = '0.1dev'

try:
    import vim
except ImportError:
    class vim:
        pass

manager = None

KEY_CACHE = {}

def init():
    import logging
    from .manager import Manager

    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    global manager
    manager = Manager()
    manager.init()

def expand(name):
    return vim.eval('expand("{}")'.format(name))

def get_key_code(key):
    try:
        return KEY_CACHE[key]
    except KeyError:
        pass

    code = KEY_CACHE[key] = expand('\<{}>'.format(key))
    return code

def filetype_changed():
    bufn = expand('<abuf>')
    filetype = expand('<amatch>')

def event_received():
    event = vim.eval("a:event")
    print event

def test():
    import threading, time
    b = vim.current.buffer
    def work():
        for _ in range(10):
            print vim.current.window.buffer.number, vim.current.window.cursor
            vim.current.window.cursor = vim.current.window.cursor
            vim.command(':redraw')
            time.sleep(1)
    
    t = threading.Thread(target=work)
    t.start()

