from vial import vfunc, vim
from vial.utils import echo

MAX_HISTORY_SIZE = 100
VHIST = 'vial_buf_hist'
VPOS = 'vial_buf_pos'
VSWITCH = 'vial_buf_switch'

def delete_from_history():
    bufnr = int(vfunc.expand('<abuf>'))

    for w in vim.windows:
        if VHIST in w.vars:
            w.vars[VHIST] = [r for r in w.vars[VHIST] if r != bufnr]


def add_to_history():
    w = vim.current.window

    if w.vars.get(VSWITCH, None):
        return

    history = list(w.vars.get(VHIST, []))

    bufnr = int(vfunc.expand('<abuf>'))

    history[:] = [r for r in history if r != bufnr]
    history.insert(0, bufnr)

    while len(history) > MAX_HISTORY_SIZE:
        history.pop()

    w.vars[VHIST] = history
    w.vars[VPOS] = 0


def next():
    jump(-1)


def prev():
    jump(1)


def jump(dir):
    w = vim.current.window
    pos = w.vars.get(VPOS, 0)
    hist = w.vars.get(VHIST, [])

    pos += dir
    if pos < 0:
        echo('Bufhist start')
        w.vars[VPOS] = 0
        return
    elif pos >= len(hist):
        echo('Bufhist end')
        w.vars[VPOS] = len(hist) - 1
        return

    w.vars[VPOS] = pos
    w.vars[VSWITCH] = True
    vim.command('buffer {}'.format(hist[pos]))
    w.vars[VSWITCH] = False
