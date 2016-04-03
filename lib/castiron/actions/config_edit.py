from castiron.tools import Action, register_actions

import os
import re

class G:
    all_edits = []

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
    '''
    Append to existing file or create new file.
    '''
    def __init__(self, path, skip_if, text):
        '''
        path is the file to edit or create.
        text is the text to inject.
        skip_if skips the edit when a line matches a regex pattern.
        '''
        super(Inject, self).__init__(path)
        self.skip_if_re = re.compile(skip_if)
        self.text = text
        self.needed = False

    def check(self, runner):
        return _file_contains_re(runner, self.path, self.skip_if_re)

    def perform(self, runner):
        if _file_contains_re(runner, self.path, self.skip_if_re):
            _append_text(runner, self.path, self.text)

def edits(*edits):
    G.all_edits.extend(edits)

class ConfigEditAction(Action):

    description = 'edit configuration files'
    enabled = True

    def __init__(self):
        super(ConfigEditAction, self).__init__()
        class CheckedEdit(object):
            def __init__(self, edit):
                self.edit = edit
                self.needed = False
        self.checked_edits = [CheckedEdit(edit) for edit in G.all_edits]

    def check(self, runner):
        okay = False
        for checked_edit in self.checked_edits:
            if runner.call(checked_edit.edit.check):
                okay = checked_edit.needed = True
        return okay

    def perform(self, runner, needed):
        for checked_edit in self.checked_edits:
            if checked_edit.needed:
                runner.call(checked_edit.edit.perform)
            else:
                print 'Configuration file was already changed: %s' % checked_edit.edit.path

register_actions(ConfigEditAction)
