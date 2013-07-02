from vial import vfunc, vim
from vial.utils import buffer_with_file, focus_window

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
