from time import sleep, time

from . import vfunc, vim
from .utils import get_key_code, get_key, redraw

TIME_SLICE = 0.02

waiting_loops = []


def pop():
    waiting_loops.pop().enter()


class Loop(object):
    def __init__(self, feedkeys):
        self.tasks = []
        self.handlers = {}
        self.do_release = False
        self.reenter = False
        self.feedkeys = feedkeys
        self.is_lazy = False

    def enter(self):
        self.is_lazy = vim.eval('&lazyredraw')
        while True:
            key, is_special = get_key()
            if key:
                if is_special:
                    if key in self.handlers:
                        h, a = self.handlers[key]
                        h(*a)
                else:
                    if 'print' in self.handlers:
                        h, a = self.handlers['print']
                        h(key, *a)
            else:
                t = time()
                self.reenter = True
                while self.tasks:
                    task = self.tasks.pop(0)
                    try:
                        next(task)
                    except StopIteration:
                        self.do_release = True
                    else:
                        self.tasks.append(task)

                    tt = time()
                    if tt - t > TIME_SLICE:
                        break
                else:
                    sleep(TIME_SLICE)

            if self.do_release:
                self.do_release = False

                if self.reenter:
                    waiting_loops.append(self)
                    vfunc.feedkeys(self.feedkeys)

                if self.is_lazy:
                    redraw()

                return

    def refresh(self):
        self.do_release = True
        self.reenter = True

    def exit(self):
        self.do_release = True
        self.reenter = False

    def idle(self, generator):
        self.tasks.append(generator)

    def on_key(self, key, handler, *args):
        self.handlers[get_key_code(key)] = (handler, args)

    def on_printable(self, handler, *args):
        self.handlers['print'] = (handler, args)
