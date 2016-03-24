import sys
import os

if os.path.exists('/etc/redhat-release'):
    raise Exception('Red Hat/CentOS is not yet supported.')
