import CI.builder.system

import sys

description = 'install software bundles'

class G:
    bundles = {
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

def features(bundles=[]):
    unknown_bundles = []
    for bundle in bundles:
        if bundle in G.bundles:
            CI.builder.system.features(packages=G.bundles[bundle])
        else:
            unknown_bundles.extend(bundle)
    if unknown_bundles:
        sys.stderr.write('Unknown bundle(s): %s' % ' '.join(unknown_bundles))

def actions(runner):
    pass
