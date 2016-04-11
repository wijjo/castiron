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

def add_builder(builder):
    G.builders.append(builder)
