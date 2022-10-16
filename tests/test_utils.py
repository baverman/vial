from vial import utils, vfunc, vim


def test_keys():
    rv = utils.parse_keys('<esc><cr>')
    assert rv == '\x1b\r'

    vim.command("execute 'normal!' '{}'".format(utils.parse_keys('i<cr><cr><esc>')))
    assert vim.current.window.cursor == (3, 0)


def test_get_key():
    vfunc.test_feedinput(utils.parse_keys('<up>'))
    rv = utils.get_key()
    assert rv == (u'\x80', False)

    rv = utils.get_key()
    assert rv == (b'k', False)

    rv = utils.get_key()
    assert rv == (b'u', False)

    vfunc.test_feedinput(utils.parse_keys('<cr>'))
    rv = utils.get_key()
    assert rv == (b'\r', True)
