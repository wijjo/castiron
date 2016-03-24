from castiron.tools import Action
from castiron.actions.ssh_initialize import SSH_DIR

import os

PRIVATE_KEY = os.path.join(SSH_DIR, 'id_rsa')
PUBLIC_KEY = '%s.pub' % PRIVATE_KEY

if not os.path.isfile(PRIVATE_KEY):
    @Action('SSH: generate private key')
    def implementation(runner):
        runner.run_command('ssh-keygen -t rsa -q -f %s' % PRIVATE_KEY)
        public_key = runner.read_file(PUBLIC_KEY)
        print('''
===== Paste the following to https://github.com/settings/ssh =====
%s
=====''' % public_key)
        runner.read_text('Press Enter to continue')
