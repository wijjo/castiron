from castiron.tools import Action, register_actions
import castiron.actions.system_packages

castiron.actions.system_packages.add_packages('git')

import os
import re

class G:
    repo_base_dir = os.path.expanduser('~/src')
    all_repo_urls = []
    parse_url_re = re.compile('^.*/([^/]+)\.git$')

def add_repo_urls(*repo_urls):
    G.all_repo_urls.extend(repo_urls)

class GitCloneAction(Action):

    description = 'create Git local repositories'
    enabled = True

    def __init__(self):
        super(GitCloneAction, self).__init__()
        self.clone_urls = None
        self.skip = None

    def check(self, runner):
        self.clone_urls = []
        self.skip = {}
        for url in G.all_repo_urls:
            dir_name = os.path.splitext(os.path.basename(url.split(':')[-1]))[0]
            if os.path.exists(os.path.join(G.repo_base_dir, dir_name)):
                self.skip[dir_name] = url
            else:
                self.clone_urls.append(url)
        return bool(self.clone_urls)

    def perform(self, runner, needed):
        if not os.path.exists(G.repo_base_dir):
            os.makedirs(G.repo_base_dir)
        if self.skip:
            print('Skipping Git repositories that seem to be present:')
            for dir_name in sorted(self.skip.keys()):
                print('  %s (%s)' % (dir_name, self.skip[dir_name]))
        with runner.chdir(G.repo_base_dir):
            for repo_url in self.clone_urls:
                runner.run_command('git clone %s' % repo_url)

register_actions(GitCloneAction)
