from vial import vim, ref

win_buf_enter = ref('.plugin.win_buf_enter')
jump = ref('.plugin.jump')

def init():
    vim.vars['vial_bufhist_timeout'] = 2 # seconds
    vim.vars['vial_bufhist_width'] = -20

    vim.command('noremap <silent> <Plug>VialBufHistPrev :python %s(1)<cr>' % jump)
    vim.command('noremap <silent> <Plug>VialBufHistNext :python %s(-1)<cr>' % jump)

    vim.command('augroup VialBufHist')
    vim.command('autocmd!')
    vim.command('autocmd BufWinEnter * python %s()' % win_buf_enter)
    vim.command('augroup END')
