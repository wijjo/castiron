import castiron
import castiron.builder.system

castiron.builder.system.features(
    'python-pip',
    'python-dev',
    'ipython',
)

class G:
    packages = []

def features(*packages):
    G.packages.extend(packages)

class PythonPackageAction(object):

    def __init__(self, package):
        self.package = package

    def check(self, runner):
        for line in castiron.tools.pipe_command('pip', 'show', self.package):
            if line.startswith('Version:'):
                return True
        return False

    def execute(self, runner):
        runner.run('sudo', 'pip', 'install', self.package)

    def description(self):
        return 'install Python package: %s' % self.package

@castiron.register('python', 'Python settings and packages')
def _builder(runner):
    for package in G.packages:
        yield PythonPackageAction(package)
