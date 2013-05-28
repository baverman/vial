from . import vim

class ListFormatter(object):
    def __init__(self, *args):
        self.columns = []
        self.spacing = '  '

        it = iter(args)
        for r in it:
            self.columns.append((r, next(it)))

        self.reset()

    def is_width_changed(self, items, winwidth):
        widths = [0] * len(self.columns)
        rest = winwidth - (len(self.columns) - 1) * len(self.spacing)
        for i, (fn, w) in enumerate(self.columns):
            if w == 0:
                widths[i] = max(self.widths[i], max(len(r[fn]) for r in items))
                rest -= widths[i]
            else:
                widths[i] = w
                if w > 1:
                    rest -= w

        for i, w in enumerate(widths):
            if w < 1:
                widths[i] = round(rest * w)

        if widths != self.widths:
            self.widths = widths
            return True
        else:
            return False

    def reset(self):
        self.widths = [0] * len(self.columns)
    
    def render(self, items):
        fmt = self.spacing.join('{{{}:<{}}}'.format(f[0], w) for f, w in zip(self.columns, self.widths))

        for r in items:
            yield fmt.format(*r)

class ListView(object):
    def __init__(self, formatter):
        self.items = []
        self.formatter = formatter
        self.rendered_items = 0

    def attach(self, buf, win):
        self.buf = buf
        self.win = win

    def set_columns(sell, *columns):
        self.columns = columns

    def clear(self):
        self.items[:] = []
        self.rendered_items = 0
        self.formatter.reset()

    def render(self):
        pass

    def append(self, item):
        self.items.append(item)

    def render(self, force=False):
        if force:
            self.rendered_items = 0

        items = self.items[self.rendered_items:]
        if not items:
            return self.rendered_items

        if self.formatter.is_width_changed(items, self.win.width):
            self.rendered_items = 0
            items = self.items

        self.buf[self.rendered_items:] = list(self.formatter.render(items))
        self.rendered_items = len(self.items)
        return self.rendered_items
    

