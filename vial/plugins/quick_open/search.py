import re

from os import listdir
from os.path import join, isdir

def name_startswith(what):
    def inner(name, path):
        return name.startswith(what)

    return inner

def name_endswith(what):
    def inner(name, path):
        return name.endswith(what)

    return inner

def name_match(what):
    def inner(name, path):
        return what in name

    return inner

def path_match(what):
    def inner(name, path):
        return what in path

    return inner

def get_matchers(pattern):
    return name_startswith(pattern), name_match(pattern)

def get_files(root, top, ignore_files=None, ignore_dirs=None):
    dirs_to_visit = []

    try:
        dir_list = listdir(join(root, top))
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
        for p in get_files(root, path, ignore_files, ignore_dirs):
            yield p
