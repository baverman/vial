import os
import re

from . import vim, vfunc
from .helpers import echo, echon, echom, echoerr
from .compat import bstr, sstr

EVAL_CACHE = {}


def eval_cache(expr):
    try:
        return EVAL_CACHE[expr]
    except KeyError:
        pass

    rv = EVAL_CACHE[expr] = vfunc.eval(expr)
    return rv


def get_key_code(code):
    return eval_cache(r'"{}"'.format(code))


def get_key():
    c = vfunc.VialGetKey()
    is_special = False
    if c:
        if len(c) == 1:
            is_special = ord(c) < 32
        else:
            if c[0] == 128:
                is_special = True

    return c, is_special


def redraw(clear=False):
    cmd = 'redraw'
    if clear:
        cmd += '!'

    vim.command(cmd)


def get_buf(bufnr):
    for b in vim.buffers:
        if b.number == bufnr:
            return b

    return None


def get_buf_by_name(name):
    num = vfunc.bufnr(name)
    return get_buf(num)


def get_projects():
    return get_list_var('vial_projects') or [os.getcwd()]


def get_winbuf(name):
    win = None
    buf = get_buf_by_name(name)
    if buf:
        for w in vim.windows:
            if w.valid and w.buffer == buf:
                win = w
                break

    return win, buf


def get_var(name, default=None):
    try:
        return vim.vars[bstr(name)]
    except KeyError:
        return default


def get_dvar(name):
    try:
        return vim.vars[bstr(name)]
    except KeyError:
        return vim.vars[bstr(name + '_default')]


def get_list_var(name, default=None):
    if default is None:
        default = []
    return [sstr(it) for it in get_var(name, default)]


def get_list_dvar(name):
    return [sstr(it) for it in get_dvar(name)]


def get_dict_var(name, default=None):
    if default is None:
        default = {}
    return {sstr(k): sstr(v) for k, v in get_var(name, default).items()}


def get_dict_dvar(name):
    return {sstr(k): sstr(v) for k, v in get_dvar(name).items()}


def focus_window(winnr):
    winnr = getattr(winnr, 'number', winnr)
    vim.command('{}wincmd w'.format(winnr))


def get_content(buf=None):
    buf = buf or vim.current.buffer
    return '\n'.join(buf[:])


def get_content_and_offset():
    line, pos = vim.current.window.cursor
    offset = vfunc.line2byte(line) + pos
    return get_content(), offset - 1


NOT_FILE_BUFFER_TYPES = set((b'nofile', b'help', b'quickfix'))


def buffer_with_file(buf):
    return buf.name and vfunc.buflisted(buf.number) and \
        vfunc.getbufvar(buf.number, '&buftype') not in NOT_FILE_BUFFER_TYPES


def mark(m='\''):
    vim.command('normal! m' + m)


def get_ws(line):
    return line[:len(line) - len(line.lstrip())]


def get_ws_len(line):
    return len(line) - len(line.lstrip())


def single(init, *args, **kwargs):
    def getter():
        try:
            return getter._object
        except AttributeError:
            result = getter._object = init(*args, **kwargs)
            return result

    def deleter():
        try:
            del getter._object
        except AttributeError:
            pass

    getter.delete = deleter
    return getter


class cached_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
