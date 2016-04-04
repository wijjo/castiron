from castiron.tools import castiron_bundle

import castiron.actions.ssh_initialize

import os

class G:
    authorized_keys_file = castiron.actions.ssh_initialize.config_path('authorized_keys')

class SSHAuthorizeKeyAction(object):

    # Don't overwrite the authorized_keys file.
    destructive  = True

    def __init__(self, authorized_keys_file):
        self.authorized_keys_file = authorized_keys_file

    def check(self, runner):
        return not os.path.isfile(self.authorized_keys_file)

    def perform(self, runner):
        public_key = runner.read_text('RSA public key')
        runner.write_file(self.authorized_keys_file, '%s\n' % public_key, permissions=0600)

@castiron_bundle('ssh-authorize-key', 'SSH: authorize public key')
def _initialize(runner):
    yield SSHAuthorizeKeyAction(G.authorized_keys_file)
