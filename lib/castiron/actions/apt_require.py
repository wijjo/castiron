from castiron.tools import ActionException

import sys
import os

if os.path.exists('/etc/redhat-release'):
    raise ActionException('Red Hat/CentOS is not yet supported.')
