from castiron.tools import castiron_feature

import castiron.features.system
castiron.features.system.add_packages(
    'htop',
)

@castiron_feature('administration', 'Administration: install tools')
def _initialize(runner):
    pass
