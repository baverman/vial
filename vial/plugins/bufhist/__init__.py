from vial import vim
from vial.utils import lfunc

win_buf_enter = lfunc('.plugin.win_buf_enter')
jump = lfunc('.plugin.jump')

def init():
    vim.vars['vial_bufhist_timeout'] = 2 # seconds
    vim.vars['vial_bufhist_width'] = -20

    vim.command('noremap <silent> <Plug>VialBufHistPrev :python vial.plugins.bufhist.jump(1)<cr>')
    vim.command('noremap <silent> <Plug>VialBufHistNext :python vial.plugins.bufhist.jump(-1)<cr>')

    vim.command('augroup VialBufHist')
    vim.command('autocmd!')
    vim.command('autocmd BufWinEnter * python vial.plugins.bufhist.win_buf_enter()')
    vim.command('augroup END')
