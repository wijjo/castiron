from castiron.tools import Action
import castiron.actions.system.require_debian

import os
import time

now_time = time.time()
apt_time = os.path.getmtime('/var/cache/apt') if os.path.exists('/var/cache/apt') else 0
update_interval = 7200

if int(apt_time) / update_interval < int(now_time) / update_interval:
    @Action('update and upgrade installed packages')
    def implementation(runner):
        runner.run_command('sudo apt-get update')
        runner.run_command('sudo apt-get upgrade')
