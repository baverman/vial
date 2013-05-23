from vial import vim

KEY_CACHE = {}

def expand(name):
    return vim.eval('expand("{}")'.format(name))

def get_key_code(key):
    try:
        return KEY_CACHE[key]
    except KeyError:
        pass

    code = KEY_CACHE[key] = expand('\<{}>'.format(key))
    return code

def get_key():
    c = vim.eval('VialGetKey()')
    is_special = False
    if c:
        if len(c) == 1:
            is_special = ord(c) < 32
        else:
            if c[0] == chr(128):
                is_special = True
            else:
                c = c.decode('utf-8')

    return c, is_special

def redraw(clear=False):
    cmd = 'redraw'
    if clear:
        cmd += '!'

    vim.command(cmd)

def bytestr(string):
    if isinstance(string, unicode):
        string = string.encode('utf-8')

    return string

def echo(message=None):
    if message:
        message = bytestr(message).replace("'", "''")
        vim.command("echo '{}'".format(message))
    else:
        vim.command('echo')
