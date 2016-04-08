import inspect

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
        runner.info(self.description, prefix='.'.join([self.name, 'initialize']))
        actions = self.initializer(runner)
        if actions:
            self.actions = [action for action in actions if action]

    def execute_actions(self, runner):
        num_actions = len(self.actions) if self.actions else 0
        description = self.description if self.description else '(no description)'
        message = '%s (actions=%d)' % (description, num_actions)
        runner.info(message, prefix='.'.join([self.name, 'execute']))
        if self.actions:
            action_number = 0
            for action in self.actions:
                action_number += 1
                # Run when needed or when it's harmless to rerun (non-destructive).
                execute = action.check(runner) or not getattr(action, 'destructive', False)
                prefix = '%s.action-%d' % (self.name, action_number)
                description = getattr(action, 'description', '(no description)')
                if inspect.ismethod(description):
                    description = action.description()
                message = '(%s) %s' % ('exec' if execute else 'skip', description)
                runner.info(message, prefix=prefix)
                if execute and not runner.options.dry_run:
                    action.execute(runner)

class Options(object):
    def __init__(self, dry_run=False, dumb_run=False):
        self.dry_run = dry_run
        self.dumb_run = dumb_run

class ActionException(Exception):
    pass

def execute_builder_actions(options):
    runner = castiron.runner.Runner(options)
    runner.info('===== Initializing builders ...')
    # Initialize the builders.
    for builder in G.builders:
        builder.initialize(runner)
    # Perform the actions (for dry or normal run).
    runner.info('===== Executing builder actions%s ...' % ' (dry run)' if runner.options.dry_run else '')
    for builder in G.builders:
        builder.execute_actions(runner)

class builder(object):
    '''
    @castiron.main.builder(name, description)
    decorator for registering builder initializers
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __call__(self, initializer):
        add_builder(Builder(self.name, self.description, initializer))
        return initializer

def add_builder(builder):
    G.builders.append(builder)
