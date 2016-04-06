from castiron.tools import castiron_feature

import castiron.features.system
castiron.features.system.add_packages(
    'build-essential',
    'ctags',
    'silversearcher-ag',
)

@castiron_feature('development', 'Development: install tools')
def _initialize(runner):
    pass
