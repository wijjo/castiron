from castiron.tools import castiron_bundle

# Dependencies
import castiron.actions.apt_require

import os
import time

# Globals
class G:
    # Minimum number of seconds between apt updates.
    update_interval_secs = 7200
    path_for_timestamp = '/var/cache/apt'

class AptUpgradeAction(object):

    def check(self, runner):
        # Give the go-ahead if either it would be the first update or no update has happened
        # within the current time interval.
        return (   not os.path.exists(G.path_for_timestamp)
                or (  int(time.time()) / G.update_interval_secs
                    > int(os.path.getmtime(G.path_for_timestamp)) / G.update_interval_secs))

    def perform(self, runner):
        runner.run_command('sudo apt-get update')
        runner.run_command('sudo apt-get upgrade')

@castiron_bundle('apt-upgrade', 'APT: update and upgrade installed packages')
def _initialize(runner):
    yield AptUpgradeAction()
