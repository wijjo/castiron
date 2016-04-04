import sys
import os

class G:
    bundles = []

class Bundle(object):
    def __init__(self, name, description, initializer):
        self.name = name
        self.description = description
        self.initializer = initializer
        self.actions = None
    def initialize(self, runner):
        runner.info('Bundle[%s] initialize: %s' % (self.name, self.description))
        self.actions = [action for action in self.initializer(runner)]
    def perform(self, runner):
        badge = runner.options.dry_run_badge()
        runner.info('Bundle[%s]%s: %s' % (self.name, badge, self.description))
        action_number = 0
        for action in self.actions:
            action_number += 1
            needed = action.check(runner)
            if runner.options.dumb_run or needed:
                description = getattr(action, 'description', '%s (action)' % self.description)
                if not needed and getattr(action, 'destructive', False):
                    runner.info('Action[%s-%d] skip destructive%s: %s' % (self.name, action_number, badge, description))
                else:
                    runner.info('Action[%s-%d] perform%s: %s' % (self.name, action_number, badge, description))
                if not runner.options.dry_run:
                    action.perform(runner)

class castiron_bundle(object):
    '''
    @castiron_bundle(name, description)
    decorator for registering action bundle initializers
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __call__(self, initializer):
        G.bundles.append(Bundle(self.name, self.description, initializer))
        return initializer

class Options(object):
    def __init__(self, dry_run=False, dumb_run=False):
        self.dry_run = dry_run
        self.dumb_run = dumb_run
    def dry_run_badge(self):
        return ' (dry)' if self.dry_run else ''

class ActionException(Exception):
    pass

class Runner(object):

    def __init__(self, options):
        self.options = options

    def run_command(self, command):
        if self.options.dry_run:
            self.info('Command: %s' % command)
            return
        rc = os.system(command)
        if rc != 0:
            self.error('Command filed (rc=%d): %s' % (rc, command))
            sys.exit(rc)

    def info(self, message):
        sys.stdout.write('INFO: %s\n' % message)

    def error(self, message):
        sys.stderr.write('ERROR: %s\n' % message)

    def create_directory(self, directory, permissions=None):
        if self.options.dry_run:
            self.info('Create directory: %s' % directory)
            if permissions is not None:
                self.info('Set permissions: %od' % permissions)
            return
        if os.path.exists(directory):
            self.info('Directory exists: %s' % directory)
        else:
            os.makedirs(directory)
        if permissions is not None:
            os.chmod(directory, permissions)

    def read_text(self, prompt):
        if self.options.dry_run:
            return ''
        return raw_input('%s: ' % prompt)

    def read_file(self, path):
        if self.options.dry_run:
            self.info('Read from: %s' % path)
            return '(text from %s)' % path
        with open(path) as f:
            return f.read().rstrip()

    def write_file(self, path, contents, permissions=None):
        if self.options.dry_run:
            self.info('Write %d characters to: %s' % (len(contents), path))
            if permissions is not None:
                self.info('Set permissions: %od' % permissions)
            return
        with open(path, 'w') as f:
            f.write(contents)
        if permissions is not None:
            os.chmod(path, permissions)

    def call(self, function, *args, **kwargs):
        if self.options.dry_run:
            self.info('Call: %s%s%s' % (function.__name__, args, kwargs if kwargs else ''))
            return
        function(self, *args, **kwargs)

    def chdir(self, new_dir):
        return ChangeDirectory(new_dir, dry_run=self.options.dry_run)

class ChangeDirectory(object):
    def __init__(self, new_dir, dry_run=False):
        self.new_dir = new_dir
        self.save_dir = None
        self.dry_run = dry_run
    def __enter__(self):
        if not self.dry_run:
            self.save_dir = os.getcwd()
            os.chdir(self.new_dir)
    def __exit__(self, exc_type, exc_value, traceback):
        if not self.dry_run:
            if self.save_dir:
                os.chdir(self.save_dir)

def perform_actions(options):
    runner = Runner(options)
    # Initialize the action bundles.
    for bundle in G.bundles:
        bundle.initialize(runner)
    # Perform the actions (for dry or normal run).
    for bundle in G.bundles:
        bundle.perform(runner)
