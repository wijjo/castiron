import castiron
import castiron.action.filesystem
import castiron.builder.system

import os

castiron_description = 'configure Vim user settings'

castiron.builder.system.castiron_features(packages=['vim'])

class G:
    settings = []
    inject_rc = None
    backup_directory = None

def castiron_features(settings=[], inject_rc=None, backup_directory=None):
    G.settings.extend(settings)
    if inject_rc:
        G.inject_rc = os.path.expandvars(os.path.expanduser(inject_rc))
    if backup_directory:
        G.backup_directory = os.path.expandvars(os.path.expanduser(backup_directory))

def castiron_initialize(runner):
    if G.backup_directory:
        yield castiron.action.filesystem.CreateDirectory(G.backup_directory)
    if G.settings:
        yield castiron.action.filesystem.InjectText('~/.vimrc', '"castiron: custom', G.settings)
    if G.inject_rc:
        yield castiron.action.filesystem.InjectText('~/.vimrc', '"castiron: private', ['source %s' % G.inject_rc])
