import castiron
import castiron.builder.system

castiron.builder.system.castiron_features(
    packages=[
        'python-pip',
        'python-dev',
        'ipython',
    ]
)

castiron_description = 'Python settings and packages'

class G:
    packages = []

def castiron_features(packages=[]):
    G.packages.extend(packages)

class PythonPackageAction(object):

    def __init__(self, package):
        self.package = package

    def check(self, runner):
        for line in castiron.tools.pipe_command('pip', 'show', self.package):
            if line.startswith('Version:'):
                return True
        return False

    def perform(self, runner):
        runner.run('sudo', 'pip', 'install', '-q', self.package)

    def description(self):
        return 'install Python package: %s' % self.package

def castiron_initialize(runner):
    for package in G.packages:
        yield PythonPackageAction(package)
