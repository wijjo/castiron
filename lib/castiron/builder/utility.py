from castiron.tools import castiron_builder

import castiron.builder.system

import sys

class G:
    tools = {
        'fast-search'        : ['silversearcher-ag'],
        'fast-compression'   : ['pbzip2', 'pigz', 'pixz', 'pxz'],
        'other-compression'  : ['zip', 'unzip', 'p7zip'],
        'pipe-viewer'        : ['pv'],
        'package-management' : ['aptitude'],
        'remote-sessions'    : ['screen', 'tmux'],
        'process-management' : ['htop'],
        'network-management' : ['curl'],
    }

def features(*names):
    unknown = []
    for name in names:
        if name in G.tools:
            castiron.builder.system.add_packages(*G.tools[name])
        else:
            unknown.extend(name)
    if unknown:
        sys.stderr.write('Unknown utility features: %s' % ' '.join(unknown))

@castiron_builder('utility', 'install utility programs')
def _initialize(runner):
    pass
