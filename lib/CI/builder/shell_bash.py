import CI
import CI.builder.system

description = 'configure Bash user settings'

features = CI.Features(
    inject_rc      = CI.File(),
    inject_profile = CI.File(),
)

CI.builder.system.features.packages = [
    'bash-completion'
]

def actions(runner):
    if features.inject_rc:
        yield CI.action.InjectText('~/.bashrc', '#CASTIRON# inject',
                                   ['source %s' % features.inject_rc])
    if features.inject_profile:
        yield CI.action.InjectText('~/.bash_profile', '#CASTIRON# inject',
                                   ['source %s' % features.inject_profile])
