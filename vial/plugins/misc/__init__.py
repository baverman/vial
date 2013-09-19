import vial
from vial.utils import lfunc

def init():
    vial.register_command('VialEscape', lfunc('.plugin.escape'))
    vial.register_command('VialSearchOutline', lfunc('.plugin.search_outline'))

    vial.register_function('VialIndent()', lfunc('.plugin.indent'))
