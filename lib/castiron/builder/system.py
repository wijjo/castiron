from castiron.tools import castiron_builder, ActionException
from castiron.action.filesystem import CreateLink, CopyFile

import sys
import os
import time

if os.path.exists('/etc/redhat-release'):
    raise ActionException('Red Hat/CentOS is not yet supported.')

#TODO: Support yum, etc..

# Globals
class G:
    # Minimum number of seconds between apt updates.
    update_interval_secs = 7200
    path_for_timestamp = '/var/cache/apt'
    packages = []
    other_actions = []

def add_packages(*packages):
    G.packages.extend(packages)

def inputrc(inputrc, copy=True):
    path = os.path.expandvars(os.path.expanduser(inputrc))
    if copy:
        G.other_actions.append(CopyFile(path, '~/.inputrc'))
    else:
        G.other_actions.append(CreateLink(path, '~/.inputrc'))

class SystemUpgradeAction(object):

    description = 'upgrade system packages'

    def check(self, runner):
        # Give the go-ahead if either it would be the first update or no update has happened
        # within the current time interval.
        return (   not os.path.exists(G.path_for_timestamp)
                or (  int(time.time()) / G.update_interval_secs
                    > int(os.path.getmtime(G.path_for_timestamp)) / G.update_interval_secs))

    def execute(self, runner):
        runner.run_command('sudo apt-get update')
        runner.run_command('sudo apt-get upgrade')

class SystemPackagesAction(object):

    def check(self, runner):
        return bool(G.packages)

    def execute(self, runner):
        runner.run_command('sudo apt-get install %s' % ' '.join(G.packages))

    def description(self):
        return 'install %d system package(s): %s' % (len(G.packages), ' '.join(G.packages))

@castiron_builder('system', 'system settings and packages')
def _initialize(runner):
    yield SystemUpgradeAction()
    if G.packages:
        yield SystemPackagesAction()
    for other_action in G.other_actions:
        yield other_action

