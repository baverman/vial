from time import time
from itertools import groupby

from vial import vfunc, vim
from vial.utils import echon, redraw
from os.path import split

MAX_HISTORY_SIZE = 100
VHIST = 'vial_buf_hist'
VLAST = 'vial_last_buf'


def add_to_history(w, bufnr):
    history = list(w.vars[VHIST])
    history[:] = [r for r in history if r != bufnr][:MAX_HISTORY_SIZE - 1]
    history.insert(0, bufnr)
    w.vars[VHIST] = history
    return history


def check_history(window):
    if not VHIST in window.vars:
        bufnr = vim.current.buffer.number
        history = [r.number for r in vim.buffers if r.number != bufnr]
        history.reverse()
        history.insert(0, bufnr)
        window.vars[VHIST] = history


def win_buf_enter():
    w = vim.current.window
    bufnr = int(vfunc.expand('<abuf>'))

    if not w.vars.get('vial_bufhist_switch', None):
        check_history(w)
        add_to_history(w, bufnr)
        w.vars[VLAST] = 0
    else:
        w.vars[VLAST] = bufnr, time()


skey = lambda r: r[1][1]
def jump(dir):
    w = vim.current.window
    check_history(w)
    history = list(w.vars[VHIST])

    bufnr = vim.current.buffer.number

    now = time()
    lastbuf = w.vars.get(VLAST, None)
    if lastbuf and bufnr == lastbuf[0] and \
            now - lastbuf[1] > vim.vars['vial_bufhist_timeout']:
        history = add_to_history(w, bufnr)

    if not bufnr in history:
        history = add_to_history(w, bufnr)

    names = {r.number: split(r.name)
        for r in vim.buffers if vfunc.buflisted(r.number)}
    history[:] = filter(lambda r: r in names, history)

    dups = True
    while dups:
        dups = False
        for name, g in groupby(sorted(names.iteritems(), key=skey), skey):
            g = list(g)
            if len(g) > 1:
                dups = True
                for nr, (path, _) in g:
                    p, n = split(path)
                    names[nr] = p, n + '/' + name

    width = vim.vars['vial_bufhist_width']
    if width < 0:
        width += int(vim.eval('&columns')) - 1

    idx = history.index(bufnr)
    idx += dir

    if idx < 0:
        idx = 0
    elif idx >= len(history):
        idx = len(history) - 1

    anr = history[idx]
    active = names[anr][1]
    before = '  '.join(names[r][1] for r in history[:idx])
    after = '  '.join(names[r][1] for r in history[idx+1:])

    half = (width - len(active) - 4) / 2
    if len(before) < len(after):
        blen = min(half, len(before))
        alen = width - len(active) - blen - 4
    else:
        alen = min(half, len(after))
        blen = width - len(active) - alen - 4

    if len(before) > blen:
        before = '...' + before[3-blen:]
    if len(after) > alen:
        after = after[:alen-3] + '...'

    if before: before += '  '
    if after: after = '  ' + after

    vim.command('let x=&ruler | let y=&showcmd')
    vim.command('set noruler noshowcmd')
    redraw()
    echon(before)
    vim.command('echohl CursorLine')
    echon(active)
    vim.command('echohl None')
    echon(after)
    vim.command('let &ruler=x | let &showcmd=y')

    if anr != bufnr:
        w.vars['vial_bufhist_switch'] = 1
        vim.command('silent b {}'.format(anr))
        w.vars['vial_bufhist_switch'] = 0
        # vim.command('augroup vial_bufhist_wait_action')
        # vim.command('au!')
        # vim.command('au CursorMoved <buffer> let
        # vim.command('augroup END')
