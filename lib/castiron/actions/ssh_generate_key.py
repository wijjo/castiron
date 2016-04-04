from castiron.tools import castiron_bundle

import castiron.actions.ssh_initialize

import os

class G:
    private_key_file = castiron.actions.ssh_initialize.config_path('id_rsa')
    public_key_file = '%s.pub' % private_key_file

class SSHGenerateKeyAction(object):

    destructive = True

    def __init__(self, private_key_file, public_key_file):
        self.private_key_file = private_key_file
        self.public_key_file = public_key_file

    def check(self, runner):
        return not os.path.isfile(self.private_key_file)

    def perform(self, runner):
        runner.run_command('ssh-keygen -t rsa -q -f %s' % self.private_key_file)
        public_key = runner.read_file(self.public_key_file)
        runner.info('===== Paste the following to https://github.com/settings/ssh =====\n%s\n=====' % public_key)
        runner.read_text('Press Enter to continue')

@castiron_bundle('ssh-generate-key', 'SSH: generate private key')
def _initialize(runner):
    yield SSHGenerateKeyAction(G.private_key_file, G.public_key_file)
