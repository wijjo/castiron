import sys
import os
import subprocess
import pipes
import textwrap

def log_message(stream, message, tag=None, contexts=None, wrap=None):
    preamble = ''.join([
        tag if tag else '',
        ' [%s]' % ' '.join(contexts) if contexts else '',
        ': ' if tag or contexts else '',
    ])
    def _display_line(s):
        if preamble:
            stream.write(preamble)
        stream.write(s)
        stream.write(os.linesep)
    if wrap is None:
        _display_line(message)
    else:
        for s in textwrap.wrap(message, wrap - len(preamble),
                               subsequent_indent='... ',
                               break_on_hyphens=False,
                               break_long_words=False):
            _display_line(s)

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

def run_command(*args):
    cmd = quote_arg_str(args)
    rc = os.system(cmd)
    if rc != 0:
        log_message(sys.stderr, 'Command failed (return code %d): %s' % (rc, cmd), tag='ERROR')
        sys.exit(rc)

def pipe_command(*args):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in iter(proc.stdout.readline, ''):
            yield line.rstrip()
        proc.stdout.close()
        rc = proc.wait()
        if rc != 0:
            log_message(sys.stderr, 'Command failed (return code %d): %s' % (rc, quote_arg_str(args)), tag='ERROR')
            sys.exit(rc)
    except Exception, e:
        log_message(sys.stderr, 'Exception running command: %s: %s' % (quote_arg_str(args)), tag='ERROR')
        sys.exit(255)
