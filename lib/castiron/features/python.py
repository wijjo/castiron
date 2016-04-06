from castiron.tools import castiron_feature

import castiron.features.system
castiron.features.system.add_packages(
    'python-pip',
    'python-dev',
    'ipython',
)

class G:
    packages = []

def add_packages(*packages):
    G.packages.extend(packages)

class PythonPackagesAction(object):

    def check(self, runner):
        return bool(G.packages)

    def execute(self, runner):
        runner.run_command('sudo pip install %s' % ' '.join(G.packages))

@castiron_feature('python-packages', 'Python: install packages')
def _initialize(runner):
    if G.packages:
        yield PythonPackagesAction()
