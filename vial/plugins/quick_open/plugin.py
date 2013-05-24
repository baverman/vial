from time import sleep

from vial import vim
from vial.utils import get_key, get_key_code, redraw, echo

def update_status(prompt):
    redraw()
    echo(u'>>> {}_'.format(prompt))

def quick_open():
    vim.command('botright split __vial_quick_open__')
    vim.command('setlocal buftype=nofile noswapfile')
    buf = vim.current.buffer
    prompt = u''
    update_status(prompt)
    while True:
        key, is_special = get_key()
        if key:
            if is_special:
                if key == get_key_code('CR') or key == get_key_code('ESC'):
                    break

                if key == get_key_code('BS'):
                    prompt = prompt[:-1]
            else:
                prompt += key

            update_status(prompt)
        else:
            sleep(0.02)

    vim.command('close')
    redraw()
    echo()

