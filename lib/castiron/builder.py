import inspect

import constants

class Builder(object):

    def __init__(self,
            name,
            module_name,
            module,
            description,
            features,
            initialize_function,
            features_function):
        self.name = name
        self.module_name = module_name
        self.module = module
        self.description = description
        self.features = features
        self.initialize_function = initialize_function
        self.features_function = features_function
        self.actions = None

    def configure(self, runner):
        runner.info('configure - %s' % self.description, contexts=[self.name], verbose=True)
        feature_dict = {}
        arg_spec = inspect.getargspec(self.features_function)
        for argi in range(len(arg_spec.args)):
            feature_dict[arg_spec.args[argi]] = arg_spec.defaults[argi]
        unknown_features = []
        for feature_name in self.features:
            if feature_name not in feature_dict:
                unknown_features.append(feature_name)
        if unknown_features:
            self.runner.fatal('Unknown %s features: %s' % (builder_module_name, ' '.join(sorted(unknown_features))))
        try:
            self.features_function(**self.features)
        except Exception, e:
            self.runner.fatal('%s.%s() exception' % (builder_module_name, constants.ATTR_FEATURES), exception=e)

    def initialize(self, runner):
        runner.info('initialize - %s' % self.description, contexts=[self.name], verbose=True)
        actions = self.initialize_function(runner)
        if actions:
            self.actions = [action for action in actions if action]

    def perform(self, runner):
        runner.info('perform - %s' % self.description, contexts=[self.name], verbose=True)
        num_actions = len(self.actions) if self.actions else 0
        description = self.description if self.description else '(no description)'
        if self.actions:
            action_number = 0
            for action in self.actions:
                # Run when needed or when it's harmless to rerun (non-destructive).
                execute = action.check(runner) or (
                            runner.options.dumb_run and not getattr(action, 'destructive', False))
                description = getattr(action, 'description', '(no description)')
                if inspect.ismethod(description):
                    description = action.description()
                if execute or runner.options.verbose:
                    if execute:
                        action_number += 1
                        label = str(action_number)
                    else:
                        label = constants.LABEL_SKIPPED
                    runner.info('action %s - %s' % (label, description), contexts=[self.name])
                if execute and not runner.options.dry_run:
                    action.perform(runner)

