import castiron
import castiron.action.filesystem
import castiron.builder.system

castiron.builder.system.features('bash-completion')

import os

class G:
    private_rc = None
    private_profile = None

def set_private_configs(private_rc, private_profile):
    G.private_rc = os.path.expandvars(os.path.expanduser(private_rc))
    G.private_profile = os.path.expandvars(os.path.expanduser(private_profile))

@castiron.register('bash', 'configure Bash user settings')
def _builder(runner):
    if G.private_rc:
        yield castiron.action.filesystem.InjectText('~/.bashrc', 'source.*bashrc', '# Private config', 'source %s' % G.private_rc)
    if G.private_profile:
        yield castiron.action.filesystem.InjectText('~/.bash_profile', 'source.*bash_profile', '# Private config', 'source %s' % G.private_profile)

