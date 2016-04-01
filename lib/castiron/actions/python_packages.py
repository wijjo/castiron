from castiron.tools import Action, register_actions
import castiron.actions.system_packages

class G:
    all_packages = []

def add_packages(*packages):
    G.all_packages.extend(packages)

class PythonPackagesAction(Action):

    description = 'install packages: Python'

    def perform(self, runner, needed):
        if G.all_packages:
            runner.run_command('sudo pip install %s' % ' '.join(G.all_packages))

register_actions(PythonPackagesAction)
