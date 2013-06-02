import sys

import vial
from vial import vim

KEY_CACHE = {}
def get_key_code(key):
    try:
        return KEY_CACHE[key]
    except KeyError:
        pass

    code = KEY_CACHE[key] = vial.vfunc.eval('"\<{}>"'.format(key))
    return code

def get_key():
    c = vial.vfunc.VialGetKey()
    is_special = False
    if c:
        if len(c) == 1:
            is_special = ord(c) < 32
        else:
            if c[0] == chr(128):
                is_special = True
            else:
                c = c.decode('utf-8')

    return c, is_special

def redraw(clear=False):
    cmd = 'redraw'
    if clear:
        cmd += '!'

    vim.command(cmd)

def bytestr(string):
    if isinstance(string, unicode):
        string = string.encode('utf-8')

    return string

def echo(message=None):
    if message:
        message = bytestr(message).replace("'", "''")
        vim.command("echo '{}'".format(message))
    else:
        vim.command('echo')

def lfunc(name):
    globs = sys._getframe(1).f_globals
    def inner(*args, **kwargs):
        try:
            func = inner.func
        except AttributeError:
            module, _, func_name = name.rpartition('.')
            module_name = module.lstrip('.')
            level = len(module) - len(module_name)

            module = __import__(module_name, globals=globs, level=level)
            if not level:
                module = sys.modules[module_name]

            try:
                func = inner.func = getattr(module, func_name)
            except AttributeError:
                raise AttributeError("module '{}' has no attribute '{}'".format(
                    module.__name__, func_name))

        return func(*args, **kwargs)

    inner.__name__ = name
    return inner

def get_buf(bufnr):
    for b in vim.buffers:
        if b.number == bufnr:
            return b
    
    return None

def get_winbuf(name):
    win = None
    num = vial.vfunc.bufnr(name)
    buf = get_buf(num)
    if buf:
        for w in vim.windows:
            if w.buffer == buf:
                win = w
                break

    return win, buf

def get_var(name, default=None):
    try:
        return vim.vars[name]
    except KeyError:
        return default

def focus_window(winnr):
    vim.command('{}wincmd w'.format(winnr))


class Func(object):
    def __init__(self):
        self._cache = {}

    def __getattr__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            pass

        func = self._cache[name] = vim.bindeval('function("{}")'.format(name))
        return func

vial.vfunc = Func()
