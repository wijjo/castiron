import sys
import os
import shutil

from tools import ChangeDirectory, log_message

class G:
    wrap_width = 100

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
        log_message(sys.stdout, message, tag='INFO', wrap=G.wrap_width, **kwargs)

    def error(self, message, **kwargs):
        log_message(sys.stderr, message, tag='ERROR', wrap=G.wrap_width, **kwargs)

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
