from castiron.tools import castiron_feature, ActionException
from castiron.actions.filesystem import CreateLink

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
    packages = [
        'aptitude',
        'screen',
    ]
    inputrc = None

def add_packages(*packages):
    G.packages.extend(packages)

def set_inputrc(inputrc):
    G.inputrc = os.path.expandvars(os.path.expanduser(inputrc))

class SystemUpgradeAction(object):

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

@castiron_feature('system', 'System: configure settings and packages')
def _initialize(runner):
    yield SystemUpgradeAction()
    if G.packages:
        yield SystemPackagesAction()
    if G.inputrc:
        yield CreateLink(G.inputrc, '~/.inputrc')

