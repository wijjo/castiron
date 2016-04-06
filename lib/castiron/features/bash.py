from castiron.tools import castiron_feature
from castiron.actions.filesystem import InjectText

import castiron.features.system
castiron.features.system.add_packages('bash-completion')

import os

class G:
    private_rc = None
    private_profile = None

def set_private_configs(private_rc, private_profile):
    G.private_rc = os.path.expandvars(os.path.expanduser(private_rc))
    G.private_profile = os.path.expandvars(os.path.expanduser(private_profile))

@castiron_feature('bash-setup', 'Bash: configure for user')
def _initialize(runner):
    if G.private_rc:
        yield InjectText('~/.bashrc', 'source.*bashrc', '# Private config', 'source %s' % G.private_rc)
    if G.private_profile:
        yield InjectText('~/.bash_profile', 'source.*bash_profile', '# Private config', 'source %s' % G.private_profile)

