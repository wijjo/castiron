import CI
import CI.builder.system

description = 'configure Vim user settings'

features = CI.Features(
    settings         = CI.List(CI.String()),
    inject_rc        = CI.File(),
    backup_directory = CI.Directory(),
)

CI.builder.system.features.packages = [
    'vim',
]

def actions(runner):
    if features.backup_directory:
        yield CI.action.CreateDirectory(features.backup_directory)
    if features.settings:
        yield CI.action.InjectText('~/.vimrc', '"castiron: custom', features.settings)
    if features.inject_rc:
        yield CI.action.InjectText('~/.vimrc', '"castiron: private', ['source %s' % features.inject_rc])
