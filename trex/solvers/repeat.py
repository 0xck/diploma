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
solver for repeating test
"""
from ..helper import FuncProperty, TypeProperty
from ..exceptions import SolverError


class Solver():
    """solver class for repeating test"""

    tries = FuncProperty('tries', lambda x: int(x) > 0)
    store = TypeProperty('store', bool)

    def __init__(self, *args, tries=1, store=False, **kwargs):

        self.tries = tries
        self.store = store

    def _decr_try(self):
        # decreases number of tries

        self.tries -= 1
        return self.tries

    def __call__(self, hub, params, *args, **kwargs):
        """general solver function

        checks if test result with certain rate is successful

        args:
            hub (list): list of processed by default processor tests result
            params (dict): params of latest test
            args: nothing

        kwargs: nothing

        return:
            (None): if tries count exhausted
            params (dict): if tries count > 0
        """
        if not self._decr_try() <= 0:
            return None

        try:
            # no need previos test data only current
            if not self.store:
                hub.pop(0)
        except (SyntaxError, IndexError) as err:
            raise SolverError(err.args) from err

        return params
