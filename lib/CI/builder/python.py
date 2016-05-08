import CI.builder.system

CI.builder.system.features(
    packages=[
        'python-pip',
        'python-dev',
        'ipython',
    ]
)

description = 'Python settings and packages'

class G:
    packages = []

def features(packages=[]):
    G.packages.extend(packages)

class PythonPackageAction(object):

    def __init__(self, package):
        self.package = package

    def check(self, runner):
        for line in runner.pipe('pip', 'show', self.package):
            if line.startswith('Version:'):
                return True
        return False

    def perform(self, runner):
        runner.run('sudo', 'pip', 'install', '-q', self.package)

    def description(self):
        return 'install Python package: %s' % self.package

def actions(runner):
    for package in G.packages:
        yield PythonPackageAction(package)
