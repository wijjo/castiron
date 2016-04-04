from castiron.tools import castiron_bundle

import os

class G:
    ssh_dir = os.path.expanduser('~/.ssh')

def config_path(path):
    return os.path.join(G.ssh_dir, path)

class SSHInitializeAction(object):

    def __init__(self, ssh_dir):
        self.ssh_dir = ssh_dir

    def check(self, runner):
        return not os.path.exists(self.ssh_dir)

    def perform(self, runner):
        # Create directory and or change the permissions, as appropriate.
        runner.create_directory(self.ssh_dir, permissions=0700)

@castiron_bundle('ssh-initialize', 'SSH: initialize user')
def _initialize(runner):
    yield SSHInitializeAction(G.ssh_dir)
