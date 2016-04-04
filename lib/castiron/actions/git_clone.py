from castiron.tools import castiron_bundle

# Make sure git is installed.
import castiron.actions.system_packages
castiron.actions.system_packages.add('git')

import os

class G:
    repo_base_dir = os.path.expanduser('~/src')
    all_repo_urls = []

def add(*repo_urls):
    G.all_repo_urls.extend(repo_urls)

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

    def perform(self, runner):
        if not os.path.exists(G.repo_base_dir):
            os.makedirs(G.repo_base_dir)
        with runner.chdir(G.repo_base_dir):
            runner.run_command('git clone %s' % repo_url)

@castiron_bundle('git-clone', 'Git: create local repositories')
def _initialize(runner):
    for repo_url in G.all_repo_urls:
        yield GitCloneAction(repo_url)
