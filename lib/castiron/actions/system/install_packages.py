from castiron.tools import Action
import castiron.actions.system.apt_update

PACKAGES = []

def add_packages(*packages):
    PACKAGES.extend(packages)

@Action('install packages: base')
def implementation(runner):
    if PACKAGES:
        runner.run_command('sudo apt-get install %s' % ' '.join(PACKAGES))
