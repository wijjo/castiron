from castiron.tools import castiron_bundle

import castiron.actions.apt_update

class G:
    packages = []

def add(*packages):
    G.packages.extend(packages)

class SystemPackagesAction(object):

    def __init__(self, packages):
        self.packages = packages

    def check(self, runner):
        return bool(self.packages)

    def perform(self, runner):
        runner.run_command('sudo apt-get install %s' % ' '.join(self.packages))

@castiron_bundle('system-packages', 'System: install packages')
def _initialize(runner):
    yield SystemPackagesAction(G.packages)
