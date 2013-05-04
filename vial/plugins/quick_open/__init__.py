from time import sleep
from vial import manager, vim, get_key_code

def init():
    manager.register_command('VialQuickOpen', quick_open)

def update_status(prompt):
    manager.redraw()
    print u'>>> {}_'.format(prompt)

def quick_open():
    vim.command('botright split __vial_quick_open__')
    vim.command('setlocal buftype=nofile')
    buf = vim.current.buffer
    prompt = u''
    update_status(prompt)
    while True:
        c = vim.eval('VialGetKey()')
        if c:
            if c == get_key_code('CR') or c == get_key_code('ESC'):
                break

            if c == get_key_code('BS'):
                prompt = prompt[:-1]
            else:
                if len(c) > 1:
                    if c[0] == chr(128):
                        continue

                    prompt += c.decode('utf-8')
                else:
                    prompt += c

            update_status(prompt)
        else:
            sleep(0.02)

    vim.command('close')
    manager.redraw()
    print

