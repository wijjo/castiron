from castiron.tools import Action, register_actions
import castiron.actions.ssh_initialize

import os

class G:
    authorized_keys_file = os.path.join(actions.ssh_directory.SSH_DIR, 'authorized_keys')

class SSHAuthorizeKeyAction(Action):

    description = 'SSH: authorize public key'

    def check(self, runner):
        return not os.path.isfile(G.authorized_keys_file)

    def perform(self, runner, needed):
        if needed:
            public_key = runner.read_text('RSA public key')
            runner.write_file(G.authorized_keys_file, '%s\n' % public_key, permissions=0600)

register_actions(SSHAuthorizeKeyAction)
