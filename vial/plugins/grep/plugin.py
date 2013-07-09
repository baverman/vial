import os
import re

from time import time

from vial import vfunc, vim
from vial.fsearch import get_files
from vial.utils import get_projects, redraw

MAX_FILESIZE = 10 * 1024 * 1024

def grep(query):
    matcher = re.compile(re.escape(query))

    t = time() - 1
    result = []
    for r in get_projects():
        for name, path, root, top, fullpath in get_files(r):
            if time() - t >= 1:
                redraw()
                print fullpath
                t = time()

            if os.stat(fullpath).st_size > MAX_FILESIZE:
                continue

            with open(fullpath) as f:
                source = f.read()
                matches = matcher.finditer(source)
                lines = source.splitlines()

            for m in matches:
                start = m.start()
                line = source.count('\n', 0, start) + 1
                offset = start - source.rfind('\n', 0, start)
                text = lines[line - 1]

                result.append({
                    'bufnr': '',
                    'filename': fullpath,
                    'pattern': '',
                    'valid': 1,
                    'nr': -1,
                    'lnum': line,
                    'vcol': 0,
                    'col': offset,
                    'text': text.replace('\x00', ' '),
                    'type': ''
                })
                
    vfunc.setqflist(result, 'r')

    if result:
        vim.command('cw')

    redraw()
    print '{} matches found'.format(len(result))
