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
            raise SolverError(err.args)

        return params
