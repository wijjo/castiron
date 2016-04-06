from castiron.tools import castiron_feature
from castiron.actions.filesystem import InjectText, CreateDirectory, CreateLink

import castiron.features.system
castiron.features.system.add_packages('vim')

class G:
    settings = []
    vimrc = None

def add_custom_configuration(*settings):
    G.settings.extend(settings)

def set_vimrc(vimrc):
    G.vimrc = vimrc

@castiron_feature('vim', 'Vim: configure user settings')
def _initialize(runner):
    yield CreateDirectory('~/.backup')
    if G.settings:
        yield InjectText('~/.vimrc', '"castiron: custom', '"castiron: custom', *G.settings)
    if G.vimrc:
        yield InjectText('~/.vimrc', '"castiron: private', '"castiron: private', 'source %s' % G.vimrc)
