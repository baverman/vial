import vial
from vial.utils import lfunc

win_buf_enter = lfunc('.plugin.win_buf_enter')
delete_from_history = lfunc('.plugin.delete_from_history')

def init():
    vial.register_command('VialBufHistNext', lfunc('.plugin.next'))
    vial.register_command('VialBufHistPrev', lfunc('.plugin.prev'))

    vial.vim.command('augroup VialBufHist')
    vial.vim.command('autocmd!')
    vial.vim.command('autocmd BufWinEnter * python vial.plugins.bufhist.win_buf_enter()')
    # vial.vim.command('autocmd BufDelete * python vial.plugins.bufhist.delete_from_history()')
    vial.vim.command('augroup END')
