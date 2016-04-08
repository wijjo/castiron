import castiron.main

import castiron.builder.system
castiron.builder.system.add_packages(
    'build-essential',
    'ctags',
)

@castiron.main.builder('development', 'install development tools')
def _initialize(runner):
    pass
