from castiron.tools import Action, register_actions

import os

SSH_DIR = os.path.expanduser('~/.ssh')

class SSHInitializeAction(Action):

    description = 'SSH: create directory'

    def check(self, runner):
        return not os.path.exists(SSH_DIR)

    def perform(self, runner, needed):
        runner.create_directory(SSH_DIR, permissions=0700)

register_actions(SSHInitializeAction)
