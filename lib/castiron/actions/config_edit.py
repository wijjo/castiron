from castiron.tools import castiron_bundle

import os
import re

class G:
    all_edits = []

def add(*edits):
    G.all_edits.extend(edits)

def _file_contains_re(runner, path, contains_re):
    real_path = os.path.realpath(os.path.expanduser(path))
    if os.path.exists(real_path):
        with open(real_path) as f:
            for line in f:
                if contains_re.search(line.rstrip()):
                    return True
    return False

def _append_text(runner, path, text):
    real_path = os.path.realpath(os.path.expanduser(path))
    with open(real_path, 'a' if os.path.exists(real_path) else 'w') as f:
        f.write('\n')
        f.write(text)
        if not text.endswith('\n'):
            f.write('\n')

class EditBase(object):
    def __init__(self, path):
        self.path = path

class Inject(EditBase):

    # Don't re-inject the text if it's already there.
    destructive = True

    def __init__(self, path, skip_if, text):
        '''
        path is the file to edit or create.
        text is the text to inject.
        skip_if skips the edit when a line matches a regex pattern.
        '''
        super(Inject, self).__init__(path)
        self.description = 'Config: inject text into file: %s' % self.path
        self.skip_if_re = re.compile(skip_if)
        self.text = text

    def check(self, runner):
        return _file_contains_re(runner, self.path, self.skip_if_re)

    def perform(self, runner):
        _append_text(runner, self.path, self.text)

@castiron_bundle('config-edit', 'Config: edit files')
def _initialize(options):
    return G.all_edits
