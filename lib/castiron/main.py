import sys
import inspect
import yaml

import castiron.runner

class G:
    builders = []

class Builder(object):

    def __init__(self, name, description, initializer):
        self.name = name
        self.description = description
        self.initializer = initializer
        self.actions = None

    def initialize(self, runner):
        runner.info(self.description, contexts=[self.name, 'initialize'])
        actions = self.initializer(runner)
        if actions:
            self.actions = [action for action in actions if action]

    def execute_actions(self, runner):
        num_actions = len(self.actions) if self.actions else 0
        description = self.description if self.description else '(no description)'
        runner.info(description, contexts=[self.name, 'execute'])
        if self.actions:
            action_number = 0
            for action in self.actions:
                action_number += 1
                # Run when needed or when it's harmless to rerun (non-destructive).
                execute = action.check(runner) or (
                            runner.options.dumb_run and not getattr(action, 'destructive', False))
                description = getattr(action, 'description', '(no description)')
                if inspect.ismethod(description):
                    description = action.description()
                if execute or runner.options.verbose:
                    contexts = [self.name, 'action', str(action_number)]
                    if not execute:
                        contexts.append('(skip)')
                    runner.info(description, contexts=contexts)
                if execute and not runner.options.dry_run:
                    action.execute(runner)

class Options(object):
    def __init__(self, dry_run=False, dumb_run=False, verbose=False):
        self.dry_run = dry_run
        self.dumb_run = dumb_run
        self.verbose = verbose

def execute_builder_actions(runner):
    runner.info('===== Initializing builders ...')
    # Initialize the builders.
    for builder in G.builders:
        builder.initialize(runner)
    # Perform the actions (for dry or normal run).
    runner.info('===== Executing builder actions%s ...' % ' (dry run)' if runner.options.dry_run else '')
    for builder in G.builders:
        builder.execute_actions(runner)

def add_builder(builder):
    G.builders.append(builder)

def load_config_yaml(runner, config_path):
    with open(config_path) as f:
        builders = yaml.load(f.read())
        for builder_name in builders:
            builder_module_name = 'castiron.builder.%(builder_name)s' % locals()
            features = builders[builder_name]
            runner.verbose_info('Import builder: %s' % builder_module_name)
            exec 'import %(builder_module_name)s as builder_module' % locals()
            feature_dict = {}
            if hasattr(builder_module, 'features'):
                arg_spec = inspect.getargspec(builder_module.features)
                for argi in range(len(arg_spec.args)):
                    feature_dict[arg_spec.args[argi]] = arg_spec.defaults[argi]
            else:
                feature_dict = {}
            unknown_features = []
            for feature_name in features:
                if feature_name not in feature_dict:
                    unknown_features.append(feature_name)
            if unknown_features:
                runner.fatal('Unknown %s features: %s' % (builder_module_name, ' '.join(sorted(unknown_features))))
            try:
                builder_module.features(**features)
            except Exception, e:
                runner.fatal('%s.features() exception[%s]: %s' % (builder_module_name, e.__class__.__name__, str(e)))
        builder_module = None

def load_config_python(runner, config_path):
    execfile(config_path)

def load_config(runner, config_path):
    try:
        if config_path.endswith('.py'):
            load_config_python(runner, config_path)
        else:
            load_config_yaml(runner, config_path)
    except Exception, e:
        runner.fatal('Failed to read configuration: %s: exception[%s]: %s' % (config_path, e.__class__.__name__, str(e)))

def main(config_path, dry_run=False, dumb_run=False, verbose=False):
    options = Options(dry_run=dry_run, dumb_run=dumb_run, verbose=verbose)
    runner = castiron.runner.Runner(options)
    load_config(runner, config_path)
    try:
        execute_builder_actions(runner)
    except castiron.ActionException, e:
        sys.stderr.write('Action error: %s\n' % str(e))
        sys.exit(255)

class register(object):
    '''
    @castiron.register(name, description)
    decorator for registering builder initializers
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __call__(self, initializer):
        add_builder(Builder(self.name, self.description, initializer))
        return initializer

class ActionException(Exception):
    pass
