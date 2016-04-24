import os

def file_has_line(runner, path, marker):
    real_path = os.path.realpath(os.path.expanduser(path))
    if os.path.exists(real_path):
        with open(real_path) as f:
            for line in f:
                if line.find(marker) >= 0:
                    return True
    return False

def inject_text(runner, path, text, permissions=None):
    real_path = os.path.realpath(os.path.expanduser(path))
    with open(real_path, 'a' if os.path.exists(real_path) else 'w') as f:
        f.write('\n')
        f.write(text)
        if not text.endswith('\n'):
            f.write('\n')
    if permissions is not None:
        os.chmod(real_path, permissions)

class OpBase(object):
    def __init__(self, path, description):
        self.path = os.path.expanduser(os.path.expandvars(path))
        self.description = description

class InjectText(OpBase):

    # Don't reinject the text if it's already there.
    destructive = True

    def __init__(self, path, marker, lines, permissions=None):
        '''
        path is the file to edit or create.
        marker skips the edit when a line matches.
        lines are the text lines to inject.
        permissions is an optional permission mask for the file
        '''
        self.marker = marker
        self.lines = lines
        self.permissions = permissions
        super(InjectText, self).__init__(path, 'inject text into file: %s' % path)

    def check(self, runner):
        return file_has_line(runner, self.path, self.marker)

    def perform(self, runner):
        inject_text(runner, self.path, '\n'.join(self.lines), permissions=self.permissions)

class CopyFile(OpBase):

    def __init__(self, source, path, overwrite=False, permissions=None, create_directory=False):
        self.source = source
        self.overwrite = overwrite
        self.permissions = permissions
        self.create_directory = create_directory
        super(CopyFile, self).__init__(path, 'copy file from "%s" to "%s"' % (source, path))

    def check(self, runner):
        return (   (not os.path.exists(self.path) or self.overwrite)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def perform(self, runner):
        runner.copy_file(self.source, self.path,
                         overwrite=self.overwrite,
                         permissions=self.permissions,
                         create_directory=self.create_directory)

class CreateLink(OpBase):

    def __init__(self, source, path):
        self.source = source
        super(CreateLink, self).__init__(path, 'create link from "%s" to "%s"' % (source, path))

    def check(self, runner):
        return not os.path.exists(self.path)

    def perform(self, runner):
        runner.create_link(self.source, self.path)

class CreateDirectory(OpBase):

    def __init__(self, path, permissions=None):
        self.permissions = permissions
        super(CreateDirectory, self).__init__(path, 'create directory "%s"' % path)

    def check(self, runner):
        return (   not os.path.exists(self.path)
                or (    self.permissions is not None
                    and self.permissions != oct(os.stat(self.path).st_mode & 0777)))

    def perform(self, runner):
        runner.create_directory(self.path, permissions=self.permissions)
