import sys

from tools import ModuleLoadHooker, ActionException
from builder import Builder
from castiron import constants

class Supervisor(object):

    def __init__(self, runner, builder_config):
        self.runner = runner
        self.builder_config = builder_config
        self.builders = []

    def load(self):
        imported_builder_names = []
        sequenced_builder_names = []
        def callback(full_name, path):
            if full_name.startswith('%s.' % constants.BUILDER_PREFIX):
                builder_name = full_name[len(constants.BUILDER_PREFIX) + 1:]
                if builder_name in self.builder_config:
                    imported_builder_names.append(builder_name)
        with ModuleLoadHooker(callback):
            for builder_name in self.builder_config:
                builder_module_name = '.'.join([constants.BUILDER_PREFIX, builder_name])
                self.runner.info('Import builder: %s' % builder_module_name, verbose=True)
                import_builder(self.runner, builder_module_name)
                if imported_builder_names:
                    # Reverse the modules imported due to dependencies so that they
                    # get invoked before the dependent modules.
                    sequenced_builder_names.extend(reversed(imported_builder_names))
                    imported_builder_names = []
        # Create the builder objects
        for builder_name in sequenced_builder_names:
            builder_module_name = '.'.join([constants.BUILDER_PREFIX, builder_name])
            builder_module = sys.modules[builder_module_name]
            if builder_module:
                missing_attributes = []
                def get_attribute(name):
                    if hasattr(builder_module, name):
                        return getattr(builder_module, name)
                    missing_attributes.append(name)
                description = get_attribute(constants.ATTR_DESCRIPTION)
                initialize_function = get_attribute(constants.ATTR_ACTIONS)
                features_function = get_attribute(constants.ATTR_FEATURES)
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
        except ActionException, e:
            sys.stderr.write('Action error: %s\n' % str(e))
            sys.exit(255)

def import_builder(runner, builder_module_name):
    try:
        exec 'import %s' % builder_module_name
    except ImportError, e:
        runner.fatal('Builder import failed: %s' % builder_module_name, exception=e)
