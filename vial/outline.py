from vial import vim, vfunc
from vial.widgets import SearchDialog, ListFormatter, ListView
from vial.utils import focus_window

dialog = None
def show(items):
    global dialog
    if not dialog:
        dialog = Outline()

    dialog.open(items)

def get_outline(items):
    result = []

    def push_childs(pf, plevel, parent):
        def inner(item):
            level = item['level']
            if level == plevel:
                item['parent'] = parent 
                item['path'] = parent + (item['name'],)
                result.append(item)
                return inner
            elif level > plevel:
                return push_childs(inner, level, result[-1]['path'])(item)
            else:
                return pf(item)

        return inner

    pf = push_childs(None, 0, ())
    for item in items:
        pf = pf(item)

    return result

class Outline(SearchDialog):
    def __init__(self):
        self.items = []
        view = ListView(self.items, ListFormatter(1,0, 2,1))
        SearchDialog.__init__(self, '__outline__', view)

    def fill(self):
        self.list_view.clear()
        for item in self.outline:
            self.items.append((item, '  ' * item['level'] + item['name'], ''))

        self.list_view.render()
        self.loop.refresh()

    def on_select(self, item, cursor):
        focus_window(self.last_window)

        item = item[0]
        if 'offset' in item:
            line = vfunc.byte2line(item['offset'] + 1)
        else:
            line = item['line']

        vim.command('normal! {}Gzz'.format(line))

    def on_cancel(self):
        focus_window(self.last_window)

    def open(self, items):
        self.last_window = vfunc.winnr()
        self.outline = get_outline(items)
        self.show('')
        self.fill()
        self.loop.enter()

    def search(self, prompt):
        self.list_view.clear()
        matchers =[
            lambda r: r.startswith(prompt),
            lambda r: prompt in r,
            lambda r: r.lower().startswith(prompt),
            lambda r: prompt in r.lower()
        ]

        already_matched = {}
        for m in matchers:
            for item in self.outline:
                n = item['name']
                p = item['parent']

                key = item.get('offset')
                if key is None:
                    key = item['line']

                if key not in already_matched and m(n):
                    already_matched[key] = True
                    self.items.append((item, n, ' / '.join(p)))

        self.list_view.render()
        self.loop.refresh()

    def on_prompt_changed(self, prompt):
        if prompt:
            self.search(prompt)
        else:
            self.fill()
