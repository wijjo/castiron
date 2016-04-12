import castiron
import castiron.builder.system

import os

castiron.builder.system.features('fish')

class FishSetupAction(object):
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

    def execute(self, runner):
        if self.fish_path:
            runner.run('sudo', 'chsh', '-s', self.fish_path, os.getlogin())

@castiron.register('shell_fish', 'configure the Fish shell')
def _builder(runner):
    yield FishSetupAction()
