import CI.builder.system

description = 'install software bundles'

features = CI.Features(
    bundles = CI.List(CI.String()),
)

class G:
    available_bundles = {
        'fast_search'          : ['silversearcher-ag'],
        'fast_compression'     : ['pbzip2', 'pigz', 'pixz', 'pxz'],
        'other_compression'    : ['zip', 'unzip', 'p7zip'],
        'pipe_viewer'          : ['pv'],
        'package_management'   : ['aptitude'],
        'remote_sessions'      : ['screen', 'tmux'],
        'process_management'   : ['htop'],
        'network_management'   : ['curl'],
        'software_development' : ['build-essential', 'ctags'],
    }

def dependencies(runner):
    unknown_bundles = []
    packages = []
    for bundle in features.bundles:
        if bundle in G.available_bundles:
            packages.extend(G.available_bundles[bundle])
        else:
            unknown_bundles.extend(bundle)
    if unknown_bundles:
        runner.error('Unknown bundle(s): %s' % ' '.join(unknown_bundles))
    if packages:
        CI.builder.system.features.packages = packages

def actions(runner):
    pass
