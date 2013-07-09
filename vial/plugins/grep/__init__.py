import vial
from vial.utils import lfunc

def init():
    vial.register_command('VialGrep', lfunc('.plugin.grep'), nargs=1)

    vial.register_function('VialGrepOperator(type)', lfunc('.plugin.grepop'))
    vial.vim.command('nnoremap <Plug>VialGrep :set operatorfunc=VialGrepOperator<cr>g@')
    vial.vim.command('vnoremap <Plug>VialGrep :<c-u>call VialGrepOperator(visualmode())<cr>')

