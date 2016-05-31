import sys
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

def main(config_path, args):
    options = Options(dry_run=args.dry_run,
                      unoptimized=args.unoptimized,
                      verbose=args.verbose,
                      debug=args.debug)
    if options.debug:
        sys.setrecursionlimit(50)
    runner = Runner(options)
    builder_config = load_configuration(runner, config_path)
    supervisor = Supervisor(runner, builder_config)
    supervisor.run()
