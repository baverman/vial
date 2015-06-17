import os
import re

from . import vim, vfunc
from .helpers import echo, echon, echom, echoerr


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


def get_buf(bufnr):
    for b in vim.buffers:
        if b.number == bufnr:
            return b

    return None


def get_buf_by_name(name):
    num = vfunc.bufnr(name)
    return get_buf(num)


def get_projects():
    return get_var('vial_projects') or [os.getcwd()]


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
        return vim.vars[name]
    except KeyError:
        return default


def get_dvar(name):
    try:
        return vim.vars[name]
    except KeyError:
        return vim.vars[name + '_default']


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
