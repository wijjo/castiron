class Options(object):
    def __init__(self, dry_run=False, unoptimized=False, verbose=False, debug=False):
        self.dry_run = dry_run
        self.unoptimized = unoptimized
        self.verbose = verbose
        self.debug = debug
