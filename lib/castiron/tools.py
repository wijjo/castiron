import sys
import os

class G:
    all_action_classes = []

def register_actions(*action_classes):
    G.all_action_classes.extend(action_classes)

class Options(object):
    def __init__(self, dry_run=False, ignore_checks=False):
        self.dry_run = dry_run
        self.ignore_checks = ignore_checks

class ActionException(Exception):
    pass

class Action(object):
    '''
    Action classes provide implementions for system changes.

    Actions must implement perform() to make changes.

    Actions can optionally implement check() when it is possible to detect
    wheen when changes are unnecessary.

    Calls to perform() should work properly even if check() returned False.
    This will happen when the --ignore-checks option is used.

    Actions should avoid changing system state in a way that interferes with
    other actions, e.g. by changing the working directory.

    Whenever possible, implementations should invoke Runner methods to enact
    changes since they are written to properly handle dry runs.
    '''
    description = None
    def __init__(self):
        if self.description is None:
            self.description = '(action class: %s)' % self.__class__.__name__
    def check(self, runner):
        return True
    def perform(self, runner, needed):
        raise Exception('Action subclass missing perform() method: %s' % self.__class__.__name__)

class Runner(object):

    def __init__(self, options):
        self.options = options

    def run_command(self, command):
        if self.options.dry_run:
            print('run: %s' % command)
            return
        rc = os.system(command)
        if rc != 0:
            self.error('Command filed (rc=%d): %s' % (rc, command))
            sys.exit(rc)

    def info(self, message):
        print(message)

    def error(self, message):
        sys.stderr.write('ERROR: %s\n' % message)

    def create_directory(self, directory, permissions=None):
        if self.options.dry_run:
            print('create directory: %s' % directory)
            if permissions is not None:
                print('set permissions: %od' % permissions)
            return
        if os.path.exists(directory):
            print('directory exists: %s' % directory)
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
            print('read from: %s' % path)
            return '(text from %s)' % path
        with open(path) as f:
            return f.read().rstrip()

    def write_file(self, path, contents, permissions=None):
        if self.options.dry_run:
            print('write %d characters to: %s' % (len(contents), path))
            if permissions is not None:
                print('set permissions: %od' % permissions)
            return
        with open(path, 'w') as f:
            f.write(contents)
        if permissions is not None:
            os.chmod(path, permissions)

    def call(self, function, *args, **kwargs):
        if self.options.dry_run:
            print('call: %s%s%s' % (function.__name__, args, kwargs if kwargs else ''))
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
    class ActionToPerform(object):
        def __init__(self, action, needed):
            self.action = action
            self.needed = needed
    needed_actions = []
    for action_class in G.all_action_classes:
        action = action_class()
        if action.check(runner):
            print('Add action: %s' % action.description)
            needed_actions.append(ActionToPerform(action, True))
        else:
            if options.ignore_checks:
                print('Add action: %s  (would be skipped without --ignore-checks)' % action.description)
                needed_actions.append(ActionToPerform(action, False))
            else:
                print('Skip action: %s' % action.description)
    for action_to_perform in needed_actions:
        print('Perform action: %s' % action_to_perform.action.description)
        action_to_perform.action.perform(runner, action_to_perform.needed)

