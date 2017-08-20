import vial


def init():
    vial.register_command('VialEscape', '.plugin.escape')
    vial.register_command('VialSearchOutline', '.plugin.search_outline')
    vial.register_command('VialChangedProjects', '.plugin.changed_projects')
    vial.register_command('VialNew', '.plugin.new', complete='file', nargs=1)
    vial.register_command('VialFilterqf', '.plugin.filter_qf', nargs=1)
    vial.register_command('VialAddProjects', '.plugin.add_projects',
                          complete='dir', bang=True, nargs='*')
    vial.register_command('VialAddIgnoreExtension',
                          '.plugin.add_ignore_extensions', bang=True, nargs='*')
    vial.register_command('VialAddIgnoreDirs', '.plugin.add_ignore_dirs',
                          complete='dir', bang=True, nargs='*')
    vial.register_command('VialReloadPlugin', '.plugin.reload_plugin', nargs=1)

    vial.register_function('VialIndent()', '.plugin.indent')

