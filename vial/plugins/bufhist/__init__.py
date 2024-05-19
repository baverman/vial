from vial import vim, ref, python_version

win_buf_enter = ref('.plugin.win_buf_enter')
jump = ref('.plugin.jump')


def init():
    vim.vars['vial_bufhist_timeout'] = 2  # seconds
    vim.vars['vial_bufhist_width'] = -20

    vim.command('noremap <silent> <Plug>VialBufHistPrev :%s %s(1)<cr>' % (python_version, jump))
    vim.command('noremap <silent> <Plug>VialBufHistNext :%s %s(-1)<cr>' % (python_version, jump))

    vim.command('augroup VialBufHist')
    vim.command('autocmd!')
    vim.command('autocmd BufWinEnter * %s %s()' % (python_version, win_buf_enter))
    vim.command('augroup END')
