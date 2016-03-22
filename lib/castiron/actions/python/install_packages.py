from castiron.tools import Action
import castiron.actions.system.install_packages

PACKAGES = []

def add_packages(*packages):
    PACKAGES.extend(packages)

@Action('install packages: Python')
def implementation(runner):
    if PACKAGES:
        runner.run_command('sudo pip install %s' % ' '.join(PACKAGES))
