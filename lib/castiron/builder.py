import inspect

from castiron import constants

class Builder(object):

    def __init__(self, name, module, config, mod_name, mod_desc, mod_actions, mod_features):
        self.name = name
        self.module = module
        self.config = config
        self.mod_name = mod_name
        self.mod_desc = mod_desc
        self.mod_actions = mod_actions
        self.mod_features = mod_features
        self.actions = None

    def configure(self, runner):
        runner.info('configure - %s' % self.mod_desc, contexts=[self.name], verbose=True)
        if inspect.isfunction(self.mod_features):
            self.configure_features_function(runner)
        else:
            try:
                self.mod_features.update(**self.config)
            except Exception, e:
                runner.fatal('%s.%s error' % (self.mod_name, constants.ATTR_FEATURES),
                                  exception=e)

    def configure_features_function(self, runner):
        feature_dict = {}
        arg_spec = inspect.getargspec(self.mod_features)
        for argi in range(len(arg_spec.args)):
            feature_dict[arg_spec.args[argi]] = arg_spec.defaults[argi]
        unknown_features = []
        for feature_name in self.config:
            if feature_name not in feature_dict:
                unknown_features.append(feature_name)
        if unknown_features:
            feature_list = ' '.join(sorted(unknown_features))
            self.runner.fatal('Unknown %s config: %s' % (self.mod_name, feature_list))
        try:
            self.mod_features(**self.config)
        except Exception, e:
            self.runner.fatal('%s.%s() error' % (self.mod_name, constants.ATTR_FEATURES),
                              exception=e)

    def initialize(self, runner):
        runner.info('initialize - %s' % self.mod_desc, contexts=[self.name], verbose=True)
        try:
            action_generator = self.mod_actions(runner)
            if action_generator:
                self.actions = [action for action in action_generator if action]
        except Exception, e:
            runner.fatal('%s.%s() error' % (self.name, constants.ATTR_ACTIONS), exception=e)

    def perform(self, runner):
        runner.info('perform - %s' % self.mod_desc, contexts=[self.name], verbose=True)
        num_actions = len(self.actions) if self.actions else 0
        mod_desc = self.mod_desc if self.mod_desc else '(no description)'
        if self.actions:
            action_number = 0
            for action in self.actions:
                # Run when needed or when it's harmless to rerun (non-destructive).
                will_run = action.check(runner)
                if not will_run and runner.options.unoptimized:
                    if getattr(action, 'destructive', False):
                        runner.info('Skipping destructive action: %s' % action.description)
                    else:
                        will_run = True
                action_desc = getattr(action, 'description', '(no description)')
                if inspect.ismethod(action_desc):
                    action_desc = action_desc()
                if will_run or runner.options.verbose:
                    if will_run:
                        action_number += 1
                        label = str(action_number)
                    else:
                        label = constants.LABEL_SKIPPED
                    runner.info('action %s - %s' % (label, action_desc), contexts=[self.name])
                if will_run and not runner.options.dry_run:
                    action.perform(runner)
