import castiron
import castiron.action.filesystem
import castiron.builder.system

import os

castiron_description = 'configure the Fish shell'

class G:
    copy_standard_config = False
    inject_private_config = None
    change_user_shell = False

def castiron_features(copy_standard_config=False, inject_private_config=None, change_user_shell=False):
    G.copy_standard_config = copy_standard_config
    if inject_private_config:
        G.inject_private_config = os.path.expandvars(os.path.expanduser(inject_private_config))
    G.change_user_shell = change_user_shell

castiron.builder.system.castiron_features(packages=['fish'])

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

def castiron_initialize(runner):
    if G.copy_standard_config:
        yield castiron.action.filesystem.CopyFile('/usr/share/fish/config.fish',
                                                  '~/.config/fish/config.fish',
                                                  overwrite=False,
                                                  permissions=None,
                                                  create_directory=True)
    if G.inject_private_config:
        yield castiron.action.filesystem.InjectText('~/.bashrc',
                                                    '#CASTIRON# Private config',
                                                    ['source %s' % G.inject_private_config])
    if G.change_user_shell:
        yield FishChangeUserShellAction()
