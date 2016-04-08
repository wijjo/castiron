import os
import textwrap

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
