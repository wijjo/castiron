import castiron
import castiron.builder.system

import sys

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
            castiron.builder.system.features(packages=G.bundles[bundle])
        else:
            unknown_bundles.extend(bundle)
    if unknown_bundles:
        sys.stderr.write('Unknown bundle(s): %s' % ' '.join(unknown_bundles))

@castiron.register('software', 'install software bundles')
def _builder(runner):
    pass
