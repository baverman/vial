import sys
import logging
import traceback

from . import vim

refs = {}


class VimFuncs(object):
    def __init__(self):
        self._cache = {}

    def __getattr__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            pass

        func = self._cache[name] = vim.bindeval('function("{}")'.format(name))
        return func
vfunc = VimFuncs()


def bytestr(string):
    if isinstance(string, unicode):
        string = string.encode('utf-8')

    return string


def _echo(cmd, message):
    if message:
        message = vfunc.escape(bytestr(message), r'\"')
        vim.command('{} "{}"'.format(cmd, message))
        vim.command(cmd)

def echo(message=None): _echo('echo', message)
def echon(message=None): _echo('echon', message)
def echom(message=None): _echo('echom', message)
def echoerr(message=None): _echo('echoerr', message)


def register_command(name, callback, **opts):
    fargs = '' if opts.get('nargs', 0) < 1 else '<f-args>'
    opts = ' '.join('-{}={}'.format(*r) for r in opts.iteritems())
    vim.command('''command! {1} {0} python {2}({3})'''.format(
        name, opts, ref(callback, 1), fargs))


def register_function(signature, callback):
    vim.command('''function! {0}
      python {1}()
      return a:result
    endfunction'''.format(signature, ref(callback, 1)))


class ref(object):
    def __init__(self, fn, depth=0):
        if isinstance(fn, basestring):
            fn = lfunc(fn, depth + 1)

        ofn = fn

        fn = getattr(fn, 'func', fn)
        if hasattr(fn, 'is_lazy'):
            line = 'lazy'
        else:
            line = fn.__code__.co_firstlineno

        name = '{}.{}:{}'.format(
            fn.__module__, fn.__name__, line)

        self.name = name
        refs[name] = ofn

    def __call__(self, *args, **kwargs):
        return refs[self.name](*args, **kwargs)

    def __str__(self):
        return "vial.refs['{}']".format(self.name)


def dref(func):
    func.ref = ref(func)
    return func


class VimLoggingHandler(logging.Handler):
    def emit(self, record):
        msg = record.getMessage()

        if record.exc_info:
            for line in traceback.format_exception(*record.exc_info):
                for l in line.rstrip().splitlines():
                    echom(l)

            msg = msg + ' ^^^'

        if record.levelno >= logging.ERROR:
            vim.command('echohl ErrorMsg')
            echom(msg)
            vim.command('echohl None')
        elif record.levelno >= logging.DEBUG:
            echom(msg)
        else:
            echo(msg)


def lfunc(name, depth=0):
    module_name, _, func_name = name.rpartition('.')
    if module_name.startswith('.'):
        globs = sys._getframe(1 + depth).f_globals
        module_name = globs['__package__'] + module_name

    def inner(*args, **kwargs):
        try:
            func = inner.func
        except AttributeError:
            __import__(module_name)
            module = sys.modules[module_name]

            try:
                func = inner.func = getattr(module, func_name)
            except AttributeError:
                raise AttributeError("module '{}' has no attribute '{}'".format(
                    module.__name__, func_name))

        return func(*args, **kwargs)

    inner.__name__ = func_name
    inner.__module__ = module_name
    inner.is_lazy = True
    return inner
