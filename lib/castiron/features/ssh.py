from castiron.tools import castiron_feature
from castiron.actions.filesystem import CreateDirectory

import os

class G:
    private_key_file = os.path.expanduser('~/.ssh/id_rsa')
    public_key_file = os.path.expanduser('~/.ssh/id_rsa.pub')
    authorized_keys_file = os.path.expanduser('~/.ssh/authorized_keys')

class SSHGenerateKeyAction(object):

    destructive = True

    def check(self, runner):
        return not os.path.isfile(G.private_key_file)

    def execute(self, runner):
        runner.run_command('ssh-keygen -t rsa -q -f %s' % G.private_key_file)
        public_key = runner.read_file(G.public_key_file)
        runner.info('===== Paste the following to https://github.com/settings/ssh =====\n%s\n=====' % public_key)
        runner.read_text('Press Enter to continue')

class SSHAuthorizeKeyAction(object):

    # Don't overwrite an existing authorized_keys file.
    destructive  = True

    def check(self, runner):
        return not os.path.isfile(G.authorized_keys_file)

    def execute(self, runner):
        public_key = runner.read_text('RSA public key')
        runner.write_file(G.authorized_keys_file, '%s\n' % public_key, permissions=0600)

@castiron_feature('ssh-generate-key', 'SSH: generate private key')
def _initialize(runner):
    yield CreateDirectory('~/.ssh', permissions=0700)
    yield SSHGenerateKeyAction()
    yield SSHAuthorizeKeyAction()
