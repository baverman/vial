import sys
import re
import os.path
import logging
import traceback

from . import vim

log = logging.getLogger(__name__)
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


def echoerr(message=None):
    vim.command('echohl ErrorMsg')
    echom(message)
    vim.command('echohl None')


def register_command(name, callback, bang=False, **opts):
    fargs = '' if opts.get('nargs', 0) == 0 else '<f-args>'
    opts = ['-{}={}'.format(k, v) if v is not True else '-{}'.format(k)
            for k, v in opts.items()]
    add = ''
    if bang:
        opts.append('-bang')
        add = '"<bang>", '

    vim.command('''command! {1} {0} python {2}({3}{4})'''.format(
        name, ' '.join(opts), ref(callback, 1), add, fargs))


args_regex = re.compile(r'(?:\(|,)\s*(\w+)')


def register_function(signature, callback):
    args = args_regex.findall(signature)
    vim.command('''function! {0}
      return pyeval("vial.helpers.vimcall({1}, {2})")
    endfunction'''.format(signature, ref(callback, 1), args))


def vimcall(func, args):
    lvars = vim.bindeval('a:')
    result = func(*[lvars[r] for r in args])
    if result is None:
        result = ''

    return result


def python(fn, *args):
    args = ', '.join(repr(r) for r in args)
    return 'python {}({})'.format(ref(fn, 1), args)


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
            echoerr(msg)
        elif record.levelno >= logging.DEBUG:
            echom(msg)
        else:
            echo(msg)


def lfunc(name, depth=0):
    module_name, _, func_name = name.rpartition('.')
    if not module_name:
        module_name = '.'

    if module_name.startswith('.'):
        globs = sys._getframe(1 + depth).f_globals
        pkg = globs['__package__']
        if module_name.strip('.'):
            module_name = pkg + module_name
        else:
            module_name = pkg

    def inner(*args, **kwargs):
        try:
            func = inner.func
        except AttributeError:
            __import__(module_name)
            module = sys.modules[module_name]

            try:
                func = inner.func = getattr(module, func_name)
            except AttributeError:
                raise AttributeError(
                    "module '{}' has no attribute '{}'".format(module.__name__,
                                                               func_name))

        return func(*args, **kwargs)

    inner.__name__ = func_name
    inner.__module__ = module_name
    inner.is_lazy = True
    return inner


def get_package(name):
    try:
        return sys.modules[name]
    except KeyError:
        __import__(name)
        return sys.modules[name]


def find_plugins(path):
    plugins = []
    pypath = []
    for p in path:
        vp = os.path.join(p, 'vial-plugin')
        if os.path.exists(vp):
            pypath.append(vp)
            for name in os.listdir(vp):
                if name.endswith('.py'):
                    plugins.append(name[:-3])
                elif os.path.exists(os.path.join(vp, name, '__init__.py')):
                    plugins.append(name)

    return plugins, pypath


class PluginManager(object):
    def __init__(self):
        self.plugins = {}

    def add_from(self, path):
        plugins, pypath = find_plugins(path)
        sys.path.extend(pypath)
        for name in plugins:
            self.add(name)

    def add(self, name):
        try:
            module = get_package(name)
        except:
            log.exception('Plugin import failed: %s', name)
            return False

        if not hasattr(module, 'init'):
            return False

        try:
            module.init()
        except:
            log.exception('Plugin init failed: %s', name)
            return False

        self.plugins[name] = module
        return True

    def addlocal(self, name):
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.append(cwd)

        return self.add(name)

    def remove(self, name):
        dotname = name + '.'
        for k in refs.keys():
            if k.startswith(dotname):
                del refs[k]

        for k in sys.modules.keys():
            if k == name or k.startswith(dotname):
                del sys.modules[k]
