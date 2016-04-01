from castiron.tools import Action, register_actions
import castiron.actions.apt_require

import os
import time

class AptUpdateAction(Action):

    description = 'update and upgrade installed packages'
    enabled = True

    update_interval = 7200

    def check(self, runner):
        now_time = time.time()
        apt_time = os.path.getmtime('/var/cache/apt') if os.path.exists('/var/cache/apt') else 0
        return int(apt_time) / self.update_interval < int(now_time) / self.update_interval

    def perform(self, runner, needed):
        runner.run_command('sudo apt-get update')
        runner.run_command('sudo apt-get upgrade')

register_actions(AptUpdateAction)
