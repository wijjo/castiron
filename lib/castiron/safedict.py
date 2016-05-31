import sys
import os
import inspect

def check_number(value):
    try:
        value + 1
    except TypeError:
        raise TypeError('Value is not an number: "%s"' % str(value))

def check_integer(value, min_value=None, max_value=None):
    check_number(value)
    if int(value) != value:
        raise TypeError('Value is not an integer: %s' % str(value))
    if min_value is not None and value < min_value:
        raise TypeError('Value is less than the minimum, %d: %d' % (min_value, value))
    if max_value is not None and value > max_value:
        raise TypeError('Value is greater than the maximum, %d: %d' % (max_value, value))

def iter_value(value):
    try:
        value + ''
        yield value
    except TypeError:
        if hasattr(value, '__iter__'):
            for v in value:
                yield v
        else:
            yield value

class SDItemType(object):
    def __init__(self, default=None):
        self.default = default
    def put(self, old_value, new_value):
        return new_value
    def check(self, value):
        pass
    def get(self, value):
        return self.default if value is None else value

class SDBoolean(SDItemType):
    def __init__(self, default=False):
        SDItemType.__init__(self, default=default)
    def check(self, value):
        if type(value) is not bool:
            raise ValueError('value is not boolean: %s' % str(value))

class SDInteger(SDItemType):
    def __init__(self, min_value=None, max_value=None, default=None):
        self.min_value = min_value
        self.max_value = max_value
        SDItemType.__init__(self, default=default)
    def check(self, value):
        check_integer(value, self.min_value, self.max_value)

class SDString(SDItemType):
    def __init__(self, default=None):
        SDItemType.__init__(self, default=default)
    def check(self, value):
        try:
            value + ''
        except TypeError:
            raise ValueError('value is not a string: %s' % str(value))

class SDList(SDItemType):
    def __init__(self, item_type, append=True, default=[]):
        self.append = append
        self.item_type = item_type
        SDItemType.__init__(self, default=default)
    def put(self, old_value, new_value):
        result = old_value if self.append else []
        for value in iter_value(new_value):
            result.append(self.item_type.put(self.item_type.default, value))
        return result
    def check(self, value):
        for item_value in value:
            self.item_type.check(item_value)

class SDDirectory(SDItemType):
    def __init__(self, exists=False, default=None):
        self.exists = exists
        SDItemType.__init__(self, default=default)
    def put(self, old_value, new_value):
        return os.path.expanduser(os.path.expandvars(new_value))
    def check(self, value):
        if not os.path.isdir(value):
            if os.path.exists(value):
                raise ValueError('path is not a directory: %s' % value)
            elif self.exists:
                raise ValueError('directory does not exist: %s' % value)
    def get(self, value):
        value2 = SDItemType.get(self, value)
        if not os.path.exists(value2):
            assert not self.exists
            try:
                os.makedirs(value2)
            except (IOError, OSError), e:
                raise ValueError('unable to create directory: %s: %s' % (value2, e.message))
        return value2

class SDFile(SDItemType):
    def __init__(self, exists=False, default=None):
        self.exists = exists
        SDItemType.__init__(self, default=default)
    def put(self, old_value, new_value):
        return os.path.expanduser(os.path.expandvars(new_value))
    def check(self, value):
        if not os.path.isfile(value):
            if os.path.exists(value):
                raise ValueError('path is not a file: %s' % value)
            elif self.exists:
                raise ValueError('file does not exist: %s' % value)

class SDURL(SDItemType):
    def __init__(self, default=None):
        SDItemType.__init__(self, default=default)
    def check(self, value):
        #TODO
        return True

class SafeDict(object):

    @classmethod
    def check_item_type_class(cls, item_type, name):
        if not hasattr(item_type, '__class__'):
            raise ValueError('"%s" is not an SDItemType subclass: non-class value' % name)
        elif not issubclass(item_type.__class__, SDItemType):
            raise ValueError('"%s" is not an SDItemType subclass: %s' % (name, item_type.__class__.__name__))

    class Impl(object):

        def __init__(self, class_name, item_type_map):
            self.class_name = class_name
            self.data = {}
            self.item_type_map = item_type_map
            for key, item_type in self.item_type_map.items():
                SafeDict.check_item_type_class(item_type, key)

        def read(self, key):
            if key not in self.item_type_map:
                raise KeyError('%s read error: bad key: %s' % (self.class_name, key))
            item_type = self.item_type_map[key]
            if not self.data.has_key(key):
                if item_type.default is not None:
                    return item_type.default
                self._raise(KeyError, key, 'read', 'value was never set')
            try:
                value = item_type.get(self.data[key])
            except ValueError, e:
                self._raise(ValueError, key, 'read', e.message)
            return value

        def write(self, key, value):
            if key not in self.item_type_map:
                self._raise(KeyError, key, 'write', 'bad key')
            item_type = self.item_type_map[key]
            try:
                item_type.check(value)
                value = item_type.put(self.data.get(key, item_type.default), value)
            except ValueError, e:
                self._raise(ValueError, key, 'write', e.message)
            self.data[key] = value

        def update(self, data):
            for key in data:
                self.write(key, data[key])

        def _raise(self, exception, key, action, message):
            raise exception('%s.%s %s error: %s' % (self.class_name, key, action, message))

    def __init__(self, **item_type_map):
        super(SafeDict, self).__setattr__('_impl', SafeDict.Impl(self.__class__.__name__, item_type_map))

    def __getitem__(self, key):
        return self._impl.read(key)

    def __setitem__(self, key, value):
        return self._impl.write(key, value)

    def __getattr__(self, key):
        return self._impl.read(key)

    def __setattr__(self, key, value):
        return self._impl.write(key, value)

    def update(self, **data):
        self._impl.update(data)

if __name__ == '__main__':

    sys.setrecursionlimit(50)

    class TestSafeDict(SafeDict):
        '''Key names start with 'p' or 'f' to indicate pass or fail expectation.'''
        def __init__(self, name, **d):
            self.name = name
            self.errors = []
            SafeDict.__init__(self, **d)
        def __getitem__(self, xkey):
            def f(key):
                return SafeDict.__getitem__(self, key)
            return self._perform(xkey, f, ' (get)')
        def __setitem__(self, xkey, value):
            def f(key):
                SafeDict.__setitem__(self, key, value)
            self._perform(xkey, f, '=%s(%s)' % (type(value).__name__, str(value)))
        def _perform(self, xkey, f, context):
            key, expect_success = xkey
            def fail(condition):
                type_name = ('unknown' if key not in sd._impl.item_type_map
                             else sd._impl.item_type_map[key].__class__.__name__)
                self.errors.append('Unexpected %s for %s %s["%s"]%s' % (
                    condition, type_name, self.name, key, context))
            try:
                ret = f(key)
                if not expect_success:
                    fail('success')
                return ret
            except (KeyError, TypeError, ValueError), e:
                if expect_success:
                    fail('%s exception' % e.__class__.__name__)
            except Exception, e:
                sys.stderr.write('%s exception: %s\n' % (e.__class__.__name__, e.message))

    sd = TestSafeDict('sd',
        i_any=SDInteger(),
        i_default_99=SDInteger(default=99),
        i_min_10=SDInteger(min_value=10),
        i_max_10=SDInteger(max_value=10),
        i_range_10_20=SDInteger(min_value=10, max_value=20),
    )

    sd['x', False] = 0
    sd['x', False]
    sd['i_any', False] = '1'
    sd['i_any', True] = 1
    sd['i_min_10', False] = 9
    sd['i_min_10', True] = 10
    sd['i_max_10', False] = 11
    sd['i_max_10', True] = 10
    sd['i_range_10_20', False] = 9
    sd['i_range_10_20', False] = 21
    sd['i_range_10_20', True] = 10
    assert(sd['i_min_10', True] == 10)
    assert(sd['i_max_10', True] == 10)
    assert(sd['i_range_10_20', True] == 10)
    assert(sd['i_default_99', True] == 99)

    print '(%d error%s)' % (len(sd.errors), 's' if len(sd.errors) != 1 else '')
    if sd.errors:
        for error in sd.errors:
            print error
        sys.exit(255)
    sys.exit(0)
