from castiron.tools import Action
import castiron.actions.ssh.create_directory

import os

AUTHORIZED_KEYS = os.path.join(actions.ssh_directory.SSH_DIR, 'authorized_keys')

if not os.path.isfile(AUTHORIZED_KEYS):
    @Action('SSH: authorize public key')
    def implementation(runner):
        public_key = runner.read_text('RSA public key')
        runner.write_file(AUTHORIZED_KEYS, '%s\n' % public_key, permissions=0600)
