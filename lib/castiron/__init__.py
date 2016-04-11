import main

class register(object):
    '''
    @castiron.register(name, description)
    decorator for registering builder initializers
    '''
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __call__(self, initializer):
        main.add_builder(main.Builder(self.name, self.description, initializer))
        return initializer

class ActionException(Exception):
    pass
