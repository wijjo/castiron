import sys

from castiron.tools import ModuleLoadHooker, ActionException
from castiron.builder import Builder
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
                mod_name = '.'.join([constants.BUILDER_PREFIX, builder_name])
                self.runner.info('Import builder: %s' % mod_name, verbose=True)
                import_builder(self.runner, mod_name)
                if imported_builder_names:
                    # Reverse the modules imported due to dependencies so that they
                    # get invoked before the dependent modules.
                    sequenced_builder_names.extend(reversed(imported_builder_names))
                    imported_builder_names = []
        for builder_name in sequenced_builder_names:
            self.add_builder(builder_name)

    def add_builder(self, name):
        mod_name = '.'.join([constants.BUILDER_PREFIX, name])
        if mod_name not in sys.modules:
            return None
        module = sys.modules[mod_name]
        config = self.builder_config[name]
        missing_attributes = []
        def get_attribute(name):
            if hasattr(module, name):
                return getattr(module, name)
            missing_attributes.append(name)
        mod_desc = get_attribute(constants.ATTR_DESCRIPTION)
        mod_actions = get_attribute(constants.ATTR_ACTIONS)
        mod_features = get_attribute(constants.ATTR_FEATURES)
        if missing_attributes:
            smissing = ' '.join(missing_attributes)
            self.runner.fatal('Builder "%s" is missing attribute(s): %s' % (mod_name, smissing))
        self.builders.append(
            Builder(name, module, config, mod_name, mod_desc, mod_actions, mod_features))

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

def import_builder(runner, mod_name):
    try:
        exec 'import %s' % mod_name
    except ImportError, e:
        runner.fatal('Builder import failed: %s' % mod_name, exception=e)
