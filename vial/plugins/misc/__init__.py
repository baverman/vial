import vial

def init():
    vial.register_command('VialEscape', '.plugin.escape')
    vial.register_command('VialSearchOutline', '.plugin.search_outline')
    vial.register_command('VialChangedProjects', '.plugin.changed_projects')
    vial.register_command('VialNew', '.plugin.new', complete='file', nargs=1)
    vial.register_command('VialFilterqf', '.plugin.filter_qf', nargs=1)
    vial.register_command('VialAddProject', '.plugin.add_project', complete='dir', nargs=1)
    vial.register_command('VialClearProjects', '.plugin.clear_projects')

    vial.register_function('VialIndent()', '.plugin.indent')
