import castiron
import castiron.action.filesystem
import castiron.builder.system

castiron.builder.system.castiron_features(packages=['bash-completion'])

castiron_description = 'configure Bash user settings'

import os

class G:
    inject_rc = None
    inject_profile = None

def castiron_features(inject_rc=None, inject_profile=None):
    if inject_rc:
        G.inject_rc = os.path.expandvars(os.path.expanduser(inject_rc))
    if inject_profile:
        G.inject_profile = os.path.expandvars(os.path.expanduser(inject_profile))

def castiron_initialize(runner):
    if G.inject_rc:
        yield castiron.action.filesystem.InjectText('~/.bashrc', '#CASTIRON# inject', ['source %s' % G.inject_rc])
    if G.inject_profile:
        yield castiron.action.filesystem.InjectText('~/.bash_profile', '#CASTIRON# inject', ['source %s' % G.inject_profile])

