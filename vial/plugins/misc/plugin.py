from vial import vfunc, vim
from vial.utils import buffer_with_file, focus_window, vimfunction

def escape():
    if len(vim.windows) < 2:
        return

    cur = vfunc.winnr()
    
    for n, w in reversed(list(enumerate(vim.windows, 1))):
        if not buffer_with_file(w.buffer):
            focus_window(n)
            vim.command('q')
            if n != cur:
                if cur > n:
                    cur -= 1

                focus_window(cur)

            return

def shift_indent(line, shift=1):
    return vfunc.indent(line-1) + shift * vfunc.eval('&sw')

@vimfunction
def indent():
    line = vim.current.window.cursor[0]
    buf = vim.current.buffer
    if buf[line-2].endswith(':'):
        return shift_indent(line)

    cline = buf[line-1].lstrip() 
    if cline and cline[0] in [')', ']', '}']:
        return shift_indent(line)

    pline = buf[line-2].rstrip() 
    if pline and pline[-1] in ['(', '[', '{']:
        return shift_indent(line)

    return -1
