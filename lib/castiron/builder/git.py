import castiron
import castiron.action.filesystem
import castiron.builder.system

castiron.builder.system.features('git')

import os

class G:
    repo_base_dir = os.path.expanduser('~/git')
    repo_urls = []
    gitconfig = None

def base_directory(base_dir):
    G.repo_base_dir = os.path.expanduser(os.path.expandvars(base_dir))

def repositories(*repo_urls):
    G.repo_urls.extend(repo_urls)

def set_gitconfig(gitconfig):
    G.gitconfig = os.path.expandvars(os.path.expanduser(gitconfig))

class GitCloneAction(object):

    # Git clone fails if directory exists.
    destructive = True

    def __init__(self, repo_url):
        self.description = 'clone Git repository: %s' % repo_url
        self.repo_url = repo_url

    def check(self, runner):
        dir_name = os.path.splitext(os.path.basename(self.repo_url.split(':')[-1]))[0]
        return not os.path.exists(os.path.join(G.repo_base_dir, dir_name))

    def execute(self, runner):
        if not os.path.exists(G.repo_base_dir):
            os.makedirs(G.repo_base_dir)
        with runner.chdir(G.repo_base_dir):
            runner.run('git', 'clone', self.repo_url)

@castiron.register('git', 'configure Git settings and local repositories')
def _builder(runner):
    if G.gitconfig:
        yield castiron.action.filesystem.CreateLink(G.gitconfig, '~/.gitconfig')
    for repo_url in G.repo_urls:
        yield GitCloneAction(repo_url)
