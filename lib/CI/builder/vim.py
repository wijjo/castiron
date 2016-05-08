import CI.action
import CI.builder.system

import os

description = 'configure Vim user settings'

CI.builder.system.features(packages=['vim'])

class G:
    settings = []
    inject_rc = None
    backup_directory = None

def features(settings=[], inject_rc=None, backup_directory=None):
    G.settings.extend(settings)
    if inject_rc:
        G.inject_rc = os.path.expandvars(os.path.expanduser(inject_rc))
    if backup_directory:
        G.backup_directory = os.path.expandvars(os.path.expanduser(backup_directory))

def actions(runner):
    if G.backup_directory:
        yield CI.action.CreateDirectory(G.backup_directory)
    if G.settings:
        yield CI.action.InjectText('~/.vimrc', '"castiron: custom', G.settings)
    if G.inject_rc:
        yield CI.action.InjectText('~/.vimrc', '"castiron: private', ['source %s' % G.inject_rc])
