"""
some ecxeptions for trex wrapper client
"""
from .helper import SEVERITY, TypeProperty


class TRexWrapperBaseError(Exception):

    level = TypeProperty('level', SEVERITY)

    """general exception

    args:
        message (str): message will be shown when the one raises
        content: additional content
    """

    def __init__(self, message, content=None, lvl=SEVERITY.NOTSET):
        self.message = message
        self.content = content
        self.level = lvl

    def get_kwargs(self):
        return {'content': self.content, 'lvl': self.level}


class TRexClientWrapperError(TRexWrapperBaseError):
    """common TRexClientWrapper exception"""
    pass


class TRexSTLClientWrapperError(TRexClientWrapperError):
    """common TRexSTLClientWrapper exception"""
    pass


class TesterError(TRexWrapperBaseError):
    """common tester exception"""
    pass


class ProcessorError(TRexWrapperBaseError):
    """common processor function exception"""
    pass


class SolverError(TRexWrapperBaseError):
    """common solver function exception"""
    pass
