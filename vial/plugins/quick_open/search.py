import re
import os

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

def path_items_startswith(pattern, skip):
    itemsp = pattern.split(os.sep)
    namep = itemsp[-1]
    itemsp = itemsp[:-1]
    count = len(itemsp)
    def inner(name, path):
        if namep and not name.startswith(namep):
            return False

        items = path.split(os.sep)
        items = items[:len(items) - 1 - skip]
        if len(items) < count:
            return False
        
        return all(i.startswith(ip) for i, ip in zip(items[-count:], itemsp))

    return inner

def path_items_match(pattern):
    itemsp = pattern.split(os.sep)
    namep = itemsp[-1]
    itemsp = itemsp[:-1]
    count = len(itemsp)
    def inner(name, path):
        if namep and not name.startswith(namep):
            return False

        items = path.split(os.sep)[:-1]
        if len(items) < count:
            return False

        return all(ip in i for i, ip in zip(items[-count:], itemsp))

    return inner

def get_matchers(pattern):
    if pattern.startswith('.'):
        return name_endswith(pattern), name_startswith(pattern),\
            name_match(pattern), path_match(pattern)
    elif os.sep in pattern:
        return path_items_startswith(pattern, 0), path_items_startswith(pattern, 1),\
            path_items_match(pattern), path_match(pattern) 

    return name_startswith(pattern), name_match(pattern), path_match(pattern)

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
