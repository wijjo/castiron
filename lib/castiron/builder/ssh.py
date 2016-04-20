import castiron
import castiron.action.filesystem

import os

PROMPT_FOR_KEY = '?'

class G:
    generate_keys = None
    private_key_path = None
    private_key_type = None
    show_public_key = None
    show_public_key_comment = None
    show_public_key_pause = None
    authorized_keys = None

def features(
        generate_keys=False,
        private_key_path='~/.ssh/id_rsa',
        private_key_type='rsa',
        show_public_key=False,
        show_public_key_comment=None,
        show_public_key_pause=False,
        # Actual public key strings and or PROMPT_FOR_KEY for prompted input.
        authorized_keys=[]
    ):
    G.generate_keys = generate_keys
    G.private_key_path = os.path.expandvars(os.path.expanduser('~/.ssh/id_rsa'))
    G.private_key_type = private_key_type
    G.show_public_key = show_public_key
    G.show_public_key_comment = show_public_key_comment
    G.show_public_key_pause = show_public_key_pause
    G.authorized_keys = authorized_keys

class GenerateKeysAction(object):

    description = 'generate an SSH private/public key pair'
    destructive = True

    def __init__(self, private_key_path, show_public_key, show_public_key_comment, show_public_key_pause):
        self.private_key_path = os.path.expandvars(os.path.expanduser(private_key_path))
        self.public_key_path = '%s.pub' % self.private_key_path
        self.show_public_key = show_public_key
        self.show_public_key_comment = show_public_key_comment
        self.show_public_key_pause = show_public_key_pause

    def check(self, runner):
        return not os.path.isfile(self.private_key_path)

    def execute(self, runner):
        runner.run('ssh-keygen', '-t', 'rsa', '-q', '-f', self.private_key_path)
        if self.show_public_key:
            public_key = runner.read_file(self.public_key_path)
            runner.info('===== Public Key =====\n%s\n=====' % public_key)
            if self.show_public_key_comment:
                runner.info(self.show_public_key_comment)
            if self.show_public_key_pause:
                runner.read_text('Press Enter to continue')

class AuthorizeKeyAction(object):

    description = 'authorize an SSH public key'
    # Don't overwrite an existing authorized_keys file.
    destructive  = True

    def __init__(self, authorized_key):
        self.authorized_key = authorized_key
        self.authorized_keys_path = os.path.expanduser('~/.ssh/authorized_keys')

    def check(self, runner):
        if self.authorized_key == PROMPT_FOR_KEY:
            return True
        return not castiron.action.filesystem.file_has_line(runner, self.authorized_keys_path, self.authorized_key)

    def execute(self, runner):
        if self.authorized_key == PROMPT_FOR_KEY:
            public_key = runner.read_text('RSA public key')
        else:
            public_key = self.authorized_key
        castiron.action.filesystem.inject_text(runner, self.authorized_keys_path, [self.authorized_key], permissions=0600)

@castiron.register('ssh', 'initialize SSH user configuration')
def _builder(runner):
    yield castiron.action.filesystem.CreateDirectory('~/.ssh', permissions=0700)
    if G.generate_keys:
        yield GenerateKeysAction(
            G.private_key_path,
            G.show_public_key,
            G.show_public_key_comment,
            G.show_public_key_pause
        )
    for authorized_key in G.authorized_keys:
        yield AuthorizeKeyAction(authorized_key)
