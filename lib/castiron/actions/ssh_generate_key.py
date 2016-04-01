from castiron.tools import Action, register_actions
from castiron.actions.ssh_initialize import SSH_DIR

import os

class G:
    private_key_file = os.path.join(SSH_DIR, 'id_rsa')
    public_key_file = '%s.pub' % private_key_file

class SSHGenerateKeyAction(Action):

    description = 'SSH: generate private key'

    def check(self, runner):
        return not os.path.isfile(G.private_key_file)

    def perform(self, runner, needed):
        if needed:
            runner.run_command('ssh-keygen -t rsa -q -f %s' % G.private_key_file)
        public_key = runner.read_file(G.public_key_file)
        print('===== Paste the following to https://github.com/settings/ssh =====\n%s\n=====' % public_key)
        runner.read_text('Press Enter to continue')

register_actions(SSHGenerateKeyAction)
