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

class PythonPackagesAction(object):

    def check(self, runner):
        return bool(G.packages)

    def execute(self, runner):
        runner.run('sudo', 'pip', 'install', ' '.join(G.packages))

    def description(self):
        return 'install %d Python package(s): %s' % (len(G.packages), ' '.join(G.packages))

@castiron.register('python', 'Python settings and packages')
def _builder(runner):
    if G.packages:
        yield PythonPackagesAction()
