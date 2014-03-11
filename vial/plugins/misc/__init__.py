import vial

def init():
    vial.register_command('VialEscape', '.plugin.escape')
    vial.register_command('VialSearchOutline', '.plugin.search_outline')

    vial.register_function('VialIndent()', '.plugin.indent')

    vial.register_command('VialChangedProjects', '.plugin.changed_projects')

    vial.register_command('VialNew', '.plugin.new', complete='file', nargs=1)
