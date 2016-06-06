import CI
import CI.builder.system

description = 'configure Git settings and local repositories'

features = CI.Features(
    base_directory  = CI.Directory(default = '~/git'),
    repository_urls = CI.List(CI.URL()),
    gitconfig       = CI.File(),
    link_gitconfig  = CI.Boolean(),
)

CI.builder.system.features.packages = [
    'git',
]

import os

class GitCloneAction(object):

    # Git clone fails if directory exists.
    destructive = True

    def __init__(self, repo_url):
        self.description = 'clone Git repository "%s"' % repo_url
        self.repo_url = repo_url

    def check(self, runner):
        dir_name = os.path.splitext(os.path.basename(self.repo_url.split(':')[-1]))[0]
        return not os.path.exists(os.path.join(features.base_directory, dir_name))

    def perform(self, runner):
        if not os.path.exists(features.base_directory):
            os.makedirs(features.base_directory)
        with runner.chdir(features.base_directory):
            runner.run('git', 'clone', self.repo_url)

def actions(runner):
    if features.gitconfig:
        if features.link_gitconfig:
            yield CI.action.CreateLink(features.gitconfig, '~/.gitconfig')
        else:
            yield CI.action.CopyFile(features.gitconfig, '~/.gitconfig')
    for repo_url in features.repository_urls:
        yield GitCloneAction(repo_url)
