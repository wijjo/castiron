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
    def __init__(self, path, description):
        self.path = os.path.expanduser(os.path.expandvars(path))
        self.description = description

class InjectText(OpBase):

    # Don't re-inject the text if it's already there.
    destructive = True

    def __init__(self, path, skip_if, *lines):
        '''
        path is the file to edit or create.
        skip_if skips the edit when a line matches a regex pattern.
        lines are the text lines to inject.
        '''
        self.skip_if_re = re.compile(skip_if)
        self.lines = lines
        super(InjectText, self).__init__(path, 'inject text into file: %s' % path)

    def check(self, runner):
        return _file_contains_re(runner, self.path, self.skip_if_re)

    def execute(self, runner):
        _append_text(runner, self.path, '\n'.join(self.lines))

class CopyFile(OpBase):

    def __init__(self, path, source, overwrite=False, permissions=None):
        self.source = source
        self.overwrite = overwrite
        self.permissions = permissions
        super(CopyFile, self).__init__(path, 'copy file from "%s" to "%s"' % (source, path))

    def check(self, runner):
        return (   (not os.path.exists(self.path) or self.overwrite)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def execute(self, runner):
        runner.copy_file(self.source, self.path, overwrite=self.overwrite, permissions=self.permissions)

class CreateLink(OpBase):

    def __init__(self, source, path):
        self.source = source
        super(CreateLink, self).__init__(path, 'create link from "%s" to "%s"' % (source, path))

    def check(self, runner):
        return not os.path.exists(self.path)

    def execute(self, runner):
        runner.create_link(self.source, self.path)

class CreateDirectory(OpBase):

    def __init__(self, path, permissions=None):
        self.permissions = permissions
        super(CreateDirectory, self).__init__(path, 'create directory "%s"' % path)

    def check(self, runner):
        return (   not os.path.exists(self.path)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def execute(self, runner):
        runner.create_directory(self.path, permissions=self.permissions)
