import sys
import os
import shutil
import inspect
import textwrap

class G:
    builders = []
    wrap_width = 100

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
                description = '(no description)' if not hasattr(action, 'description') else (
                    action.description() if inspect.ismethod(action.description) else action.description)
                message = '(%s) %s' % ('exec' if execute else 'skip', description)
                runner.info(message, prefix=prefix, wrap=G.wrap_width)
                if execute and not runner.options.dry_run:
                    action.execute(runner)

class CastironBuilderDecorator(object):
    '''
    @castiron_builder(name, description)
    decorator for registering builder initializers
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __call__(self, initializer):
        G.builders.append(Builder(self.name, self.description, initializer))
        return initializer

# @castiron_builder decorator used by builder modules to register themselves.
castiron_builder = CastironBuilderDecorator

class Options(object):
    def __init__(self, dry_run=False, dumb_run=False):
        self.dry_run = dry_run
        self.dumb_run = dumb_run

class ActionException(Exception):
    pass

def log_message(stream, message, tag=None, prefix=None, error=False, wrap=None):
    preamble = ''.join(['%s: ' % tag if tag else '',  '::%s:: ' % prefix if prefix else ''])
    def _line(s):
        if preamble:
            stream.write(preamble)
        stream.write(s)
        stream.write(os.linesep)
    if wrap is None:
        _line(message)
    else:
        for s in textwrap.wrap(message, wrap - len(preamble),
                               subsequent_indent='... ',
                               break_on_hyphens=False,
                               break_long_words=False):
            _line(s)

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

    def info(self, message, **kwargs):
        log_message(sys.stdout, message, tag='INFO', **kwargs)

    def error(self, message, **kwargs):
        log_message(sys.stderr, message, tag='ERROR', **kwargs)

    def create_directory(self, path, permissions=None):
        directory = os.path.expanduser(os.path.expandvars(path))
        if self.options.dry_run:
            self.info('Create directory: %s' % directory)
            if permissions is not None:
                self.info('Set directory permissions: %od' % permissions)
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

    def create_link(self, source, target):
        if self.options.dry_run:
            self.info('Create linke: %s -> %s' % (target, source))
            return
        if os.path.isdir(target):
            os.symlink(source, os.path.join(target, os.path.basename(source)))
            return
        if os.path.exists(target):
            self.info('Link target exists: %s' % target)
            return
        os.symlink(source, target_path)

    def copy_file(self, source, target, overwrite=False, permissions=None):
        if self.options.dry_run:
            self.info('Copy file: %s -> %s' % (target, source))
            if permissions is not None:
                self.info('Set file permissions: %od' % permissions)
            return
        if overwrite or (os.path.exists(target) and not os.path.isdir(target)):
            self.info('File exists: %s' % target)
            return
        shutil.copyfile(source, target)
        if permissions is not None:
            os.chmod(target, permissions)

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

def execute_builder_actions(options):
    runner = Runner(options)
    runner.info('===== Initializing builders ...')
    # Initialize the builders.
    for builder in G.builders:
        builder.initialize(runner)
    # Perform the actions (for dry or normal run).
    runner.info('===== Executing builder actions%s ...' % ' (dry run)' if runner.options.dry_run else '')
    for builder in G.builders:
        builder.execute_actions(runner)
