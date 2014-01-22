import os
import re
import sys

from vial import vim, vfunc

KEY_CACHE = {}
def get_key_code(key):
    try:
        return KEY_CACHE[key]
    except KeyError:
        pass

    code = KEY_CACHE[key] = vfunc.eval('"\<{}>"'.format(key))
    return code

keys_re = re.compile(r'<(.+?)>')
def replace_key_match(match):
    return get_key_code(match.group(1))

def parse_keys(keys):
    return keys_re.sub(replace_key_match, keys)

def get_key():
    c = vfunc.VialGetKey()
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

def get_buf(bufnr):
    for b in vim.buffers:
        if b.number == bufnr:
            return b

    return None

def get_projects():
    return get_var('vial_projects', [os.getcwd()])

def get_winbuf(name):
    win = None
    num = vfunc.bufnr(name)
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

def get_dvar(name):
    try:
        return vim.vars[name]
    except KeyError:
        return vim.vars[name + '_default']

def focus_window(winnr):
    vim.command('{}wincmd w'.format(winnr))

def vimfunction(func):
    from inspect import getargspec
    args = getargspec(func)[0]
    def inner():
        lvars = vim.bindeval('a:')
        result = func(*[lvars[r] for r in args])
        if result is None:
            result = ''

        lvars['result'] = result

    inner.func = func
    return inner

def get_content(buf=None):
    buf = buf or vim.current.buffer
    return '\n'.join(buf[:])

def get_content_and_offset():
    line, pos = vim.current.window.cursor
    offset = vfunc.line2byte(line) + pos
    return get_content(), offset - 1

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

NOT_FILE_BUFFER_TYPES = set(('nofile', 'help'))
def buffer_with_file(buf):
    return buf.name and vfunc.buflisted(buf.number) and \
        vfunc.getbufvar(buf.number, '&buftype') not in NOT_FILE_BUFFER_TYPES 

def mark(m='\''):
    vim.command('normal! m' + m)

def get_ws(line):
    return line[:len(line) - len(line.lstrip())]

def get_ws_len(line):
    return len(line) - len(line.lstrip())

