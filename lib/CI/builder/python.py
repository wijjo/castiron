import CI.builder.system

description = 'Python settings and packages'

features = CI.Features(
    packages = CI.List(CI.String()),
)

CI.builder.system.features.packages = [
    'python-pip',
    'python-dev',
    'ipython',
]

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
    for package in features.packages:
        yield PythonPackageAction(package)
