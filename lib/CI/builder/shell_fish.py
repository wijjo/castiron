import CI
import CI.builder.system

import os

description = 'configure the Fish shell'

features = CI.Features(
    copy_standard_config  = CI.Boolean(),
    change_user_shell     = CI.Boolean(),
)

CI.builder.system.features.packages = [
    'fish',
]

class FishChangeUserShellAction(object):
    description = "choose Fish as the user shell"

    def __init__(self):
        self.fish_path = None

    def check(self, runner):
        okay = True
        with open('/etc/passwd') as f:
            for line in f:
                fields = line.strip().split(':')
                if len(fields) > 6 and int(fields[2]) == os.getuid():
                    okay = os.path.basename(fields[6]) != 'fish'
                    #TODO: Handle non-standard locations?
                    self.fish_path = '/usr/bin/fish'
                    break
        return okay

    def perform(self, runner):
        if self.fish_path:
            runner.run('sudo', 'chsh', '-s', self.fish_path, os.getlogin())

def actions(runner):
    if features.copy_standard_config:
        yield CI.action.CopyFile('/usr/share/fish/config.fish', '~/.config/fish/config.fish',
                                 overwrite=False, permissions=None, create_directory=True)
    if features.change_user_shell:
        yield FishChangeUserShellAction()
