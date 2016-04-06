import os
import re

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

class OpBase(object):
    def __init__(self, path):
        self.path = os.path.expanduser(os.path.expandvars(path))

class InjectText(OpBase):

    # Don't re-inject the text if it's already there.
    destructive = True

    def __init__(self, path, skip_if, *lines):
        '''
        path is the file to edit or create.
        skip_if skips the edit when a line matches a regex pattern.
        lines are the text lines to inject.
        '''
        super(InjectText, self).__init__(path)
        self.description = 'File: inject text: %s' % self.path
        self.skip_if_re = re.compile(skip_if)
        self.lines = lines

    def check(self, runner):
        return _file_contains_re(runner, self.path, self.skip_if_re)

    def execute(self, runner):
        _append_text(runner, self.path, '\n'.join(self.lines))

class CreateLink(OpBase):

    def __init__(self, path, permissions=None):
        super(CreateLink, self).__init__(path)
        self.permissions = permissions

    def check(self, runner):
        return (   not os.path.exists(self.path)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def execute(self, runner):
        runner.create_directory(self.path, permissions=self.permissions)

class CreateDirectory(OpBase):

    def __init__(self, path, permissions=None):
        super(CreateDirectory, self).__init__(path)
        self.permissions = permissions

    def check(self, runner):
        return (   not os.path.exists(self.path)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def execute(self, runner):
        runner.create_directory(self.path, permissions=self.permissions)
