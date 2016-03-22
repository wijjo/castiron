from castiron.tools import Action

import os

SSH_DIR = os.path.expanduser('~/.ssh')

if not os.path.exists(SSH_DIR):
    @Action('SSH: create directory')
    def implementation(runner):
        runner.create_directory(SSH_DIR, permissions=0700)
