import sys

PY2 = sys.version_info[0] == 2

utype = type(u'')
btype = type(b'')
stype = type('')


def bstr(data, encoding='latin1'):
    if type(data) is utype:
        data = data.encode(encoding)
    return data


def ustr(data, encoding='latin1'):
    if type(data) is btype:
        data = data.decode(encoding)
    return data


def sstr(data, encoding='latin1'):
    tdata = type(data)
    if tdata is stype:
        pass
    elif tdata is utype:
        data = bstr(data, encoding)
    elif tdata is btype:
        data = ustr(data, encoding)
    return data


if PY2:  # pragma: no cover
    import __builtin__ as builtins
    filter = builtins.filter

    iterkeys = dict.iterkeys
    itervalues = dict.itervalues
    iteritems = dict.iteritems
    listkeys = dict.keys
    listvalues = dict.values
    listitems = dict.items

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')
else:  # pragma: no cover
    import builtins

    filter = lambda *args, **kwargs: list(builtins.filter(*args, **kwargs))

    iterkeys = dict.keys
    itervalues = dict.values
    iteritems = dict.items
    listkeys = lambda d: list(d.keys())
    listvalues = lambda d: list(d.values())
    listitems = lambda d: list(d.items())

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
