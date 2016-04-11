import castiron
import castiron.builder.system

castiron.builder.system.features(
    'build-essential',
    'ctags',
)

@castiron.register('development', 'install development tools')
def _initialize(runner):
    pass
