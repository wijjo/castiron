from castiron.tools import castiron_feature

import castiron.features.system
castiron.features.system.add_packages(
    'curl',
)

@castiron_feature('network', 'Network: install tools')
def _initialize(runner):
    pass
