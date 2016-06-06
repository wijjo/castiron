import CI

import os

description = 'initialize SSH user configuration'

features = CI.Features(
    generate_keys           = CI.Boolean(),
    private_key_path        = CI.File('~/.ssh/id_rsa'),
    private_key_type        = CI.String(default='rsa'),
    show_public_key         = CI.Boolean(),
    show_public_key_comment = CI.String(),
    show_public_key_pause   = CI.Boolean(),
    authorized_keys         = CI.List(CI.String(),
)

class G:
    # When specified for authorized_keys item prompts the user for the key.
    prompt_for_key_string = 'prompt'

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

    def perform(self, runner):
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
        self.injector = CI.action.InjectText(self.authorized_keys_path, self.authorized_key,
                                             [self.authorized_key], permissions=0600)

    def check(self, runner):
        if self.authorized_key == G.prompt_for_key_string:
            return True
        return self.injector.check(runner)

    def perform(self, runner):
        if self.authorized_key == G.prompt_for_key_string:
            public_key = runner.read_text('RSA public key')
        else:
            public_key = self.authorized_key
        if not public_key:
            runner.info('No RSA public key provided - skipping.')
            return
        self.injector.perform(runner)

def actions(runner):
    yield CI.action.CreateDirectory('~/.ssh', permissions=0700)
    if features.generate_keys:
        yield GenerateKeysAction(
            features.private_key_path,
            features.show_public_key,
            features.show_public_key_comment,
            features.show_public_key_pause
        )
    for authorized_key in features.authorized_keys:
        yield AuthorizeKeyAction(authorized_key)
