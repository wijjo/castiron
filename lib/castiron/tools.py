import sys
import os

functions = []

class Options(object):
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

class Action(object):
    def __init__(self, description):
        self.description = description
    def __call__(self, function):
        def wrapper(runner):
            print 'Execute: %s' % self.description
            return function(runner)
        functions.append(wrapper)
        return function

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
        os.makedirs(directory)
        if permissions is not None:
            os.chmod(directory, permissions)

    def read_text(self, prompt):
        return raw_input('%s: ' % prompt)

    def read_file(self, path):
        if self.options.dry_run:
            print('read from: %s' % path)
            return
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
