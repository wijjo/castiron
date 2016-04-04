from castiron.tools import castiron_bundle

import castiron.actions.system_packages

class G:
    all_packages = []

def add(*packages):
    G.all_packages.extend(packages)

class PythonPackagesAction(object):

    description = 'install packages: Python'

    def __init__(self, packages):
        self.packages = packages

    def check(self, runner):
        return bool(self.packages)

    def perform(self, runner):
        runner.run_command('sudo pip install %s' % ' '.join(self.packages))

@castiron_bundle('python-packages', 'Python: install packages')
def _initialize(runner):
    yield PythonPackagesAction(G.all_packages)
