import sys
import os
import subprocess
import pipes
import textwrap
import traceback

class Logger(object):

    class Writer(object):
        def __init__(self, stream, preamble):
            self.stream = stream
            self.preamble = preamble
        def __call__(self, s):
            if self.preamble:
                self.stream.write(self.preamble)
            self.stream.write(s)
            self.stream.write(os.linesep)

    def __init__(self, stream=None, tag=None, wrap=None, verbose=False, debug=False, callback=None):
        self.stream = stream if stream else sys.stdout
        self.tag = tag if tag else ''
        self.wrap = wrap
        self.verbose = verbose
        self.debug = debug
        self.callback = callback

    def __call__(self, message, contexts=None, exception=None, verbose=False, unwrapped=False):
        if verbose and not self.verbose:
            return
        preamble = ''.join([self.tag,
                           ' [%s]' % ' '.join(contexts) if contexts else '',
                           ': ' if self.tag or contexts else ''])
        write_line = Logger.Writer(self.stream, preamble)
        if unwrapped or self.wrap is None:
            write_line(message)
        else:
            for line in textwrap.wrap(message, self.wrap - len(preamble),
                                      subsequent_indent='... ',
                                      break_on_hyphens=False,
                                      break_long_words=False):
                write_line(line)
        if exception:
            write_line('Exception(%s): %s' % (exception.__class__.__name__, str(exception)))
            if self.debug:
                traceback.print_exc()
        if self.callback:
            self.callback()

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

def quote_arg_str(args):
    return ' '.join([pipes.quote(arg) for arg in args])

error = Logger(stream=sys.stderr, tag='ERROR')

def run_command(*args):
    cmd = quote_arg_str(args)
    rc = os.system(cmd)
    if rc != 0:
        error('Command failed (return code %d): %s' % (rc, cmd))
        sys.exit(rc)

def pipe_command(*args):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in iter(proc.stdout.readline, ''):
            yield line.rstrip()
        proc.stdout.close()
        rc = proc.wait()
        if rc != 0:
            error('Command failed (return code %d): %s' % (rc, quote_arg_str(args)))
            sys.exit(rc)
    except Exception, e:
        error('Exception running command: %s: %s' % (quote_arg_str(args)))
        sys.exit(255)

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

class ActionException(Exception):
    pass
