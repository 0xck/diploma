# Copyright 2017-2018 by Constantine Kormashev. All Rights Reserved.
# Licensed under Mozilla Public License Version 2.0 (the "License");
# You may obtain a copy of the License at
# https://www.mozilla.org/en-US/MPL/2.0/
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


class ExecutorError(TRexWrapperBaseError):
    """common executor function exception"""
    pass
