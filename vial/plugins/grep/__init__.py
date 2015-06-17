import vial


def init():
    vial.register_command('VialGrep', '.plugin.grep', nargs=1)

    vial.register_function('<SID>VialGrepOperator(type)', '.plugin.grepop')
    vial.vim.command('nnoremap <Plug>VialGrep :set operatorfunc=<SID>VialGrepOperator<cr>g@')
    vial.vim.command('vnoremap <Plug>VialGrep :<c-u>call <SID>VialGrepOperator(visualmode())<cr>')
