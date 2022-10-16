# coding=utf-8
import vial
from vial.compat import sstr


def test_vars():
    vial.vim.command('let g:boo = "zoo"')
    assert sstr(vial.vim.vars['boo']) == 'zoo'

    vial.vim.command('let g:unicode_var = "текст"')
    assert sstr(vial.vim.vars['unicode_var'], 'utf-8') == 'текст'
