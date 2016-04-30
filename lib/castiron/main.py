import sys
import inspect
import yaml

import castiron.runner

MODULE_PREFIX    = 'castiron.builder.'
ATTR_DESCRIPTION = 'description'
ATTR_ACTIONS     = 'actions'
ATTR_FEATURES    = 'features'
LABEL_SKIPPED    = '(skipped)'

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
        runner.verbose_info('configure - %s' % self.description, contexts=[self.name])
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
            self.runner.fatal_exception('%s.%s() exception' % builder_module_name, ATTR_FEATURES, e)

    def initialize(self, runner):
        runner.verbose_info('initialize - %s' % self.description, contexts=[self.name])
        actions = self.initialize_function(runner)
        if actions:
            self.actions = [action for action in actions if action]

    def perform(self, runner):
        runner.verbose_info('perform - %s' % self.description, contexts=[self.name])
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
                        label = LABEL_SKIPPED
                    runner.info('action %s - %s' % (label, description), contexts=[self.name])
                if execute and not runner.options.dry_run:
                    action.perform(runner)

def import_builder(runner, builder_module_name):
    exec 'import %s' % builder_module_name

class Options(object):
    def __init__(self, dry_run=False, dumb_run=False, verbose=False):
        self.dry_run = dry_run
        self.dumb_run = dumb_run
        self.verbose = verbose

class ModuleLoadHooker(object):
    def __init__(self, callback):
        self.callback = callback
    def __enter__(self):
        sys.meta_path.append(self)
    def __exit__(self, exc_type, exc_value, traceback):
        sys.meta_path.pop()
    def find_module(self, full_name, path=None):
        self.callback(full_name, path)
        return None
    def load_module(self, name):
        raise ImportError('Unexpected call to ModuleLoadHooker.load_module()')

class Supervisor(object):

    def __init__(self, runner, builder_config):
        self.runner = runner
        self.builder_config = builder_config
        self.builders = []

    def load(self):
        imported_builder_names = []
        sequenced_builder_names = []
        def callback(full_name, path):
            if full_name.startswith(MODULE_PREFIX):
                builder_name = full_name[len(MODULE_PREFIX):]
                if builder_name in self.builder_config:
                    imported_builder_names.append(builder_name)
        with ModuleLoadHooker(callback):
            for builder_name in self.builder_config:
                builder_module_name = 'castiron.builder.%(builder_name)s' % locals()
                self.runner.verbose_info('Import builder: %s' % builder_module_name)
                import_builder(self.runner, builder_module_name)
                if imported_builder_names:
                    # Reverse the modules imported due to dependencies so that they
                    # get invoked before the dependent modules.
                    sequenced_builder_names.extend(reversed(imported_builder_names))
                    imported_builder_names = []
        # Create the builder objects
        for builder_name in sequenced_builder_names:
            builder_module_name = ''.join([MODULE_PREFIX, builder_name])
            builder_module = sys.modules[builder_module_name]
            if builder_module:
                missing_attributes = []
                def get_attribute(name):
                    if hasattr(builder_module, name):
                        return getattr(builder_module, name)
                    missing_attributes.append(name)
                description = get_attribute(ATTR_DESCRIPTION)
                initialize_function = get_attribute(ATTR_ACTIONS)
                features_function = get_attribute(ATTR_FEATURES)
                if missing_attributes:
                    self.runner.fatal('Builder module "%s" missing attribute(s): %s'
                                        % (builder_module_name, ' '.join(missing_attributes)))
                self.builders.append(
                        Builder(builder_name,
                                builder_module_name,
                                builder_module,
                                description,
                                self.builder_config[builder_name],
                                initialize_function,
                                features_function))

    def configure(self):
        self.runner.info('===== Configuring builder features ...')
        for builder in self.builders:
            builder.configure(self.runner)

    def initialize(self):
        self.runner.info('===== Initializing builders ...')
        # Initialize the builders.
        for builder in self.builders:
            builder.initialize(self.runner)

    def perform(self):
        # Perform the actions (for dry or normal run).
        self.runner.info('===== Performing builder actions%s ...' % ' (dry run)' if self.runner.options.dry_run else '')
        for builder in self.builders:
            builder.perform(self.runner)

    def run(self):
        self.load()
        self.configure()
        try:
            self.initialize()
            self.perform()
        except castiron.ActionException, e:
            sys.stderr.write('Action error: %s\n' % str(e))
            sys.exit(255)

def load_configuration(runner, config_path):
    try:
        with open(config_path) as f:
            return yaml.load(f.read())
    except Exception, e:
        runner.fatal_exception('Failed to load configuration: %s' % config_path, e)

def main(config_path, dry_run=False, dumb_run=False, verbose=False):
    options = Options(dry_run=dry_run, dumb_run=dumb_run, verbose=verbose)
    runner = castiron.runner.Runner(options)
    builder_config = load_configuration(runner, config_path)
    supervisor = Supervisor(runner, builder_config)
    supervisor.run()

class ActionException(Exception):
    pass
