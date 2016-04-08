from castiron.tools import castiron_builder

import castiron.builder.system
castiron.builder.system.add_packages(
    'build-essential',
    'ctags',
)

@castiron_builder('development', 'install development tools')
def _initialize(runner):
    pass
