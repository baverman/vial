import re

from vial import vfunc, vim
from vial.fsearch import get_files
from vial.utils import get_projects

def grep(query):
    matcher = re.compile(re.escape(query))

    result = []
    for r in get_projects():
        for name, path, root, top, fullpath in get_files(r):
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
                    'text': text,
                    'type': ''
                })
                
    vfunc.setqflist(result, 'r')
    print '{} matches found'.format(len(result))
