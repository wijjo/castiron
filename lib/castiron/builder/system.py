import sys
import os
import time

import castiron
import castiron.action.filesystem

if os.path.exists('/etc/redhat-release'):
    raise castiron.ActionException('Red Hat/CentOS is not yet supported.')

#TODO: Support yum, etc..

# Globals
class G:
    # Minimum number of seconds between apt updates.
    update_interval_secs = 7200
    path_for_timestamp = '/var/cache/apt'
    # For now features are simply equivalent to Debian package names.  When Yum
    # support is added features should become universal names that get
    # translated as needed between package management systems.
    packages = []
    inputrc = None
    link_inputrc = False
    to_install = None

def features(packages=[], inputrc=None, link_inputrc=False):
    G.packages.extend(packages)
    if inputrc:
        G.inputrc = os.path.expandvars(os.path.expanduser(inputrc))
    G.link_inputrc = link_inputrc

class SystemUpgradeAction(object):

    description = 'upgrade system packages'

    def check(self, runner):
        # Give the go-ahead if either it would be the first update or no update has happened
        # within the current time interval.
        return (   not os.path.exists(G.path_for_timestamp)
                or (  int(time.time()) / G.update_interval_secs
                    > int(os.path.getmtime(G.path_for_timestamp)) / G.update_interval_secs))

    def execute(self, runner):
        runner.run('sudo', 'apt-get', '-qq', 'update')
        runner.run('sudo', 'apt-get', '-qq', 'upgrade')

class SystemPackageAction(object):

    def __init__(self, package):
        self.package = package

    def check(self, runner):
        if G.to_install is None:
            G.to_install = set()
            runner.verbose_info('Checking installed packages...')
            for line in castiron.tools.pipe_command('sudo', 'apt-get', '-sqq', 'install', *G.packages):
                fields = line.split()
                if len(fields) >= 2 and fields[0] in ('Inst', 'Conf', 'Remv'):
                    G.to_install.add(fields[1])
        return self.package in G.to_install

    def execute(self, runner):
        runner.run('sudo', 'apt-get', 'install', '-qq', self.package)

    def description(self):
        return 'install system package: %s' % self.package

@castiron.register('system', 'system settings and packages')
def _builder(runner):
    yield SystemUpgradeAction()
    for package in G.packages:
        yield SystemPackageAction(package)
    if G.inputrc:
        if G.link_inputrc:
            yield castiron.action.filesystem.CreateLink(G.inputrc, '~/.inputrc')
        else:
            yield castiron.action.filesystem.CopyFile(G.inputrc, '~/.inputrc')

