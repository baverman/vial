import vial
from vial.utils import lfunc

add_to_history = lfunc('.plugin.add_to_history')
delete_from_history = lfunc('.plugin.delete_from_history')

def init():
    vial.register_command('VialBufHistNext', lfunc('.plugin.next'))
    vial.register_command('VialBufHistPrev', lfunc('.plugin.prev'))

    vial.vim.command('augroup VialBufHist')
    vial.vim.command('autocmd!')
    vial.vim.command('autocmd BufWinEnter * python vial.plugins.bufhist.add_to_history()')
    vial.vim.command('autocmd BufDelete * python vial.plugins.bufhist.delete_from_history()')
    vial.vim.command('augroup END')
