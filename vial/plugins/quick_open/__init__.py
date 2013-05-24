from vial import manager
from vial.utils import lfunc

def init():
    manager.register_command('VialQuickOpen', lfunc('.plugin.quick_open'))

