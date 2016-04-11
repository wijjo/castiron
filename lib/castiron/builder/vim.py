import castiron
import castiron.action.filesystem
import castiron.builder.system

castiron.builder.system.features('vim')

class G:
    settings = []
    vimrc = None

def add_custom_configuration(*settings):
    G.settings.extend(settings)

def set_vimrc(vimrc):
    G.vimrc = vimrc

@castiron.register('vim', 'configure Vim user settings')
def _builder(runner):
    yield castiron.action.filesystem.CreateDirectory('~/.backup')
    if G.settings:
        yield castiron.action.filesystem.InjectText('~/.vimrc', '"castiron: custom', '"castiron: custom', *G.settings)
    if G.vimrc:
        yield castiron.action.filesystem.InjectText('~/.vimrc', '"castiron: private', '"castiron: private', 'source %s' % G.vimrc)
