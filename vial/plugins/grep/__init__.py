import vial
from vial.utils import lfunc

def init():
    vial.register_command('VialGrep', lfunc('.plugin.grep'), nargs=1)
