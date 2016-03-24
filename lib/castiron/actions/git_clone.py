from castiron.tools import Action
import castiron.actions.system_packages

import os
import re

castiron.actions.system_packages.add_packages('git')

REPO_BASE_DIR = os.path.expanduser('~/src')
REPO_URLS = []
RE_PARSE_URL = re.compile('^.*/([^/]+)\.git$')

def add_repo_urls(*repo_urls):
    for repo_url in repo_urls:
        m = RE_PARSE_URL.match(repo_url)
        if not m:
            raise Exception('Bad Git repository URL: %s' % repo_url)
        path = os.path.join(REPO_BASE_DIR, m.group(1))
        if os.path.exists(path):
            print('Skipping Git clone over existing location: %s' % path)
        else:
            REPO_URLS.append(repo_url)

@Action('create Git local repositories')
def implementation(runner):
    if not os.path.exists(REPO_BASE_DIR):
        os.mkdir(REPO_BASE_DIR)
    os.chdir(REPO_BASE_DIR)
    for repo_url in REPO_URLS:
        runner.run_command('git clone %s' % repo_url)
