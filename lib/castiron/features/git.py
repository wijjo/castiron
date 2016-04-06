from castiron.tools import castiron_feature
from castiron.actions.filesystem import CreateLink

# Make sure git is installed.
import castiron.features.system
castiron.features.system.add_packages('git')

import os

class G:
    repo_base_dir = os.path.expanduser('~/src')
    repo_urls = []
    gitconfig = None

def add_repositories(*repo_urls):
    G.repo_urls.extend(repo_urls)

def set_gitconfig(gitconfig):
    G.gitconfig = os.path.expandvars(os.path.expanduser(gitconfig))

class GitCloneAction(object):

    # Git clone fails if directory exists.
    destructive = True

    def __init__(self, repo_url):
        super(GitCloneAction, self).__init__()
        self.description = 'Git: create local repository: %s' % repo_url
        self.repo_url = repo_url

    def check(self, runner):
        dir_name = os.path.splitext(os.path.basename(self.repo_url.split(':')[-1]))[0]
        return not os.path.exists(os.path.join(G.repo_base_dir, dir_name))

    def execute(self, runner):
        if not os.path.exists(G.repo_base_dir):
            os.makedirs(G.repo_base_dir)
        with runner.chdir(G.repo_base_dir):
            runner.run_command('git clone %s' % repo_url)

@castiron_feature('git', 'Git: configure settings and local repositories')
def _initialize(runner):
    if G.gitconfig:
        yield CreateLink(G.gitconfig, '~/.gitconfig')
    for repo_url in G.repo_urls:
        yield GitCloneAction(repo_url)
