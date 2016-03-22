import actions.ssh_generate_key
import actions.install_packages
import actions.python_packages

actions.install_packages.add_packages(
    'vim',
    'build-essential',
    'ctags',
    'htop',
    'curl',
    'zip',
    'unzip',
    'p7zip',
    'pbzip2',
    'pigz',
    'pixz',
    'pv',
    'pxz',
    'ipython',
    'aptitude',
    'bash-completion',
    'silversearcher-ag',
    'python-pip',
    'python-dev',
)

actions.python_packages.add_packages(
    'pyinstaller',
)
