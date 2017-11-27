"""
some ecxeptions for trex wrapper client
"""
from helper import SEVERITY, TypeProperty


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


class TRexClientWrapperError(TRexWrapperBaseError):
    """common TRexClientWrapper exception"""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class TRexSTLClientWrapperError(TRexClientWrapperError):
    """common TRexSTLClientWrapper exception"""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class ProcessorError(TRexWrapperBaseError):
    """common processor function exception"""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class SolverError(TRexWrapperBaseError):
    """common solver function exception"""

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
