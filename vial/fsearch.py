import re

from os import listdir
from os.path import join, isdir, split

from .utils import get_dvar


def _walk(root, top, ignore_files=None, ignore_dirs=None):
    dirs_to_visit = []

    try:
        dir_list = sorted(listdir(join(root, top)), key=lambda r: (len(r), r))
    except OSError:
        pass
    else:
        for name in dir_list:
            path = join(top, name)
            fullpath = join(root, top, name)
            if isdir(fullpath):
                if not ignore_dirs or not ignore_dirs.match(path):
                    dirs_to_visit.append(path)
            else:
                if not ignore_files or not ignore_files.match(path):
                    yield name, path, root, top, fullpath

    for path in dirs_to_visit:
        for p in _walk(root, path, ignore_files, ignore_dirs):
            yield p


def get_files(root, cache=None, keep_top=False):
    if cache is not None:
        try:
            return cache[root]
        except KeyError:
            pass

    ignore_files = re.compile('.*({})$'.format(
        '|'.join(r'\.{}'.format(r)
                 for r in get_dvar('vial_ignore_extensions'))))

    ignore_dirs = re.compile('({})'.format('|'.join(
        get_dvar('vial_ignore_dirs'))))

    fcache = []
    if keep_top:
        root, top = split(root)
    else:
        root, top = root, ''

    def filler():
        for r in _walk(root, top, ignore_files, ignore_dirs):
            fcache.append(r)
            yield r

        if cache is not None:
            cache[root] = fcache

    return filler()
