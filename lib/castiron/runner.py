import sys
import os
import shutil
import copy

from tools import ChangeDirectory, log_message, quote_arg_str, pipe_command, run_command

class G:
    wrap_width = 100

def _log(stream, tag, message, **kwargs):
    if 'wrap' in kwargs:
        kwargs2 = kwargs
    else:
        kwargs2 = copy.copy(kwargs)
        kwargs2['wrap'] = G.wrap_width
    log_message(stream, message, tag=tag, **kwargs2)

class Runner(object):

    def __init__(self, options):
        self.options = options

    def run(self, *args):
        if self.options.dry_run or self.options.verbose:
            self.info('Run command: %s' % quote_arg_str(args), wrap=None)
        if self.options.dry_run:
            return
        run_command(*args)

    def pipe(self, *args):
        if self.options.dry_run or self.options.verbose:
            self.info('Pipe command: %s' % quote_arg_str(args), wrap=None)
        if self.options.dry_run:
            return
        for line in pipe_command(*args):
            yield line

    def info(self, message, **kwargs):
        _log(sys.stdout, 'INFO', message, **kwargs)

    def error(self, message, **kwargs):
        _log(sys.stderr, 'ERROR', message, **kwargs)

    def fatal(self, message, **kwargs):
        _log(sys.stderr, 'FATAL', message, **kwargs)
        sys.exit(255)

    def create_directory(self, path, permissions=None):
        directory = os.path.expanduser(os.path.expandvars(path))
        if self.options.dry_run or self.options.verbose:
            if not os.path.exists(directory):
                self.info('Create directory: %s' % directory)
        if self.options.dry_run:
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
        if self.options.dry_run or self.options.verbose:
            self.info('Read from: %s' % path)
        if self.options.dry_run:
            return '(text from %s)' % path
        with open(path) as f:
            return f.read().rstrip()

    def write_file(self, path, contents, permissions=None):
        if self.options.dry_run or self.options.verbose:
            self.info('Write %d characters to: %s' % (len(contents), path))
            if permissions is not None:
                self.info('Set permissions: %od' % permissions)
        if self.options.dry_run:
            return
        with open(path, 'w') as f:
            f.write(contents)
        if permissions is not None:
            os.chmod(path, permissions)

    def call(self, function, *args, **kwargs):
        if self.options.dry_run or self.options.verbose:
            self.info('Call: %s%s%s' % (function.__name__, args, kwargs if kwargs else ''))
        if self.options.dry_run:
            return
        function(self, *args, **kwargs)

    def chdir(self, new_dir):
        return ChangeDirectory(new_dir, dry_run=self.options.dry_run)

    def create_link(self, source, target):
        if self.options.dry_run or self.options.verbose:
            self.info('Create link: %s -> %s' % (target, source))
        if self.options.dry_run:
            return
        if os.path.isdir(target):
            os.symlink(source, os.path.join(target, os.path.basename(source)))
            return
        if os.path.exists(target):
            self.info('Link target exists: %s' % target)
            return
        os.symlink(source, target_path)

    def copy_file(self, source, target, overwrite=False, permissions=None, create_directory=False):
        if self.options.dry_run or self.options.verbose:
            self.info('Copy file: %s -> %s' % (target, source))
            if permissions is not None:
                self.info('Set file permissions: %od' % permissions)
        if self.options.dry_run:
            return
        if overwrite or (os.path.exists(target) and not os.path.isdir(target)):
            self.info('File exists: %s' % target)
            return
        if create_directory:
            self.create_directory(os.path.dirname(directory))
        shutil.copyfile(source, target)
        if permissions is not None:
            os.chmod(target, permissions)
