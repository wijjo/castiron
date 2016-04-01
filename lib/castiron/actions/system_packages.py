from castiron.tools import Action, register_actions
import castiron.actions.apt_update

class G:
    packages = []

def add_packages(*packages):
    G.packages.extend(packages)

class SystemPackagesAction(Action):

    description = 'install packages: base'

    def check(self, runner):
        return bool(G.packages)

    def perform(self, runner, needed):
        runner.run_command('sudo apt-get install %s' % ' '.join(G.packages))

register_actions(SystemPackagesAction)
