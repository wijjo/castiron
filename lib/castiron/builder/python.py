import castiron.main

import castiron.builder.system
castiron.builder.system.add_packages(
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

    def description(self):
        return 'install %d Python package(s): %s' % (len(G.packages), ' '.join(G.packages))

@castiron.main.builder('python', 'Python settings and packages')
def _builder(runner):
    if G.packages:
        yield PythonPackagesAction()
