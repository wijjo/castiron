import yaml

from castiron.runner import Runner
from castiron.supervisor import Supervisor
from castiron.options import Options

def load_configuration(runner, config_path):
    try:
        with open(config_path) as f:
            return yaml.load(f.read())
    except Exception, e:
        runner.fatal('Failed to load configuration: %s' % config_path, exception=e)

def main(config_path, dry_run=False, dumb_run=False, verbose=False):
    options = Options(dry_run=dry_run, dumb_run=dumb_run, verbose=verbose)
    runner = Runner(options)
    builder_config = load_configuration(runner, config_path)
    supervisor = Supervisor(runner, builder_config)
    supervisor.run()
