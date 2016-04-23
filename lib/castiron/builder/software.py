import castiron
import castiron.builder.system

import sys

castiron_description = 'install software bundles'

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

def castiron_features(bundles=[]):
    unknown_bundles = []
    for bundle in bundles:
        if bundle in G.bundles:
            castiron.builder.system.castiron_features(packages=G.bundles[bundle])
        else:
            unknown_bundles.extend(bundle)
    if unknown_bundles:
        sys.stderr.write('Unknown bundle(s): %s' % ' '.join(unknown_bundles))

def castiron_initialize(runner):
    pass
