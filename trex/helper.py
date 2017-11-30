"""
helper provides different objects that are used by other part of app
"""
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
from enum import Enum, IntEnum, unique


@unique
class SEVERITY(IntEnum):
    CRITICAL = CRITICAL
    ERROR = ERROR
    WARNING = WARNING
    INFO = INFO
    DEBUG = DEBUG
    NOTSET = NOTSET


@unique
class TREXMODE(Enum):
    stf = 'stf'
    stl = 'stl'


@unique
class TREXSTATUS(Enum):
    idle = 'idle'
    running = 'running'
    unavailable = 'unavailable'
    unknown = 'unknown'


class BaseProperty():
    """common class for descriptors

    makes property with certain attributes given by child
    returns and sets value for them

    args:
        attr (str): name of checked attirbute

    kwargs:
        prop (dict):
            key: name of attribute which contain control value for checking
            value: value of control attribute

            e.g. prop={'types': int} means self.types = int
            where <type int> is value for checking attr
    """

    template = 'Attribut <{}> of class <{}> item must be in {} '.format

    def __init__(self, attr, prop={}):

        if not any(prop.values()):
            raise ValueError('Property items must be defined')

        for name, val in ([name, val] for name, val in prop.items() if val):
            setattr(self, name, val)

        self.attr = ''.join(['_', attr])

    def __get__(self, obj, cls):
        return getattr(obj, self.attr)

    def __set__(self, obj, value):
        setattr(obj, self.attr, value)


class TypeProperty(BaseProperty):

    def __init__(self, attr, types):
        super().__init__(attr, prop={'types': types})

    def __set__(self, obj, value):
        if not isinstance(value, self.types):
            raise TypeError(self.template(self.attr[1:], obj.__class__.__name__, self.types))
        super().__set__(obj, value)


class ValueProperty(BaseProperty):

    def __init__(self, attr, values):
        super().__init__(attr, prop={'values': values})

    def __set__(self, obj, value):
        if value not in self.values:
            raise ValueError(self.template(self.attr[1:], obj.__class__.__name__, self.values))
        super().__set__(obj, value)


class TypeValueProperty(TypeProperty, ValueProperty):

    def __init__(self, attr, types, values):
        BaseProperty.__init__(self, attr, prop={'types': types, 'values': values})

    def __set__(self, obj, value):
        super().__set__(obj, value)


class Result():
    """common result obj"""

    status = TypeProperty('status', bool)

    def __init__(self, status=False, value=None, error=None):
        self.status = status
        self.value = value
        self.error = error

    def success(self):
        self.status = True

    def fail(self):
        self.status = False

    def set_err(self, error):
        self.fail()
        self.error = error
        self.value = None
        return self

    def set_val(self, value):
        self.success()
        self.value = value
        self.error = None
        return self

    def set_all(self, status, value, error):
        self.status = status
        self.value = value
        self.error = error
        return self

    def __bool__(self):
        return self.status