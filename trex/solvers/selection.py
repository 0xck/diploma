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
solver tries to find suit test rate for given parameters

used simple logical model:
R is rate has to be set
RS is rate step for in-/decrease rate
CR is current rate
PR is previos rate
D is drops/lossed occured in latest test (that is not within norm)

CR > PR and D is False --> R = R + RS
CR > PR and D is True --> R = PR
CR <= PR and D is False --> R = PR
CR <= PR and D is True --> R = R - RS
"""

from enum import Enum, unique
from functools import wraps, partial
from ..helper import TREXMODE, ValueProperty, FuncProperty, TypeProperty, firstfilter
from ..exceptions import ProcessorError, SolverError


@unique
class CHECKTYPE(Enum):
    """
    'safe' for checking accurancy and drops
    'accuracy' for checking accurancy only
    'drop' for checking drop only
    """

    safe = 'safe'
    accuracy = 'accuracy'
    drop = 'drop'


@unique
class RATEKEY(Enum):
    """
    'multiplier' for stf
    'rate' for stl
    """

    multiplier = 'm'
    rate = 'rate'


class Solver():
    """docstring for Solver"""

    check_type = ValueProperty('check_type', CHECKTYPE)
    step = TypeProperty('step', (int, float))
    max_succ = FuncProperty('max_succ', lambda x: int(x) >= 0)
    store = TypeProperty('store', bool)

    def __init__(self, accuracy=0.001, step=1, max_succ=3, mode=None, check_type=CHECKTYPE.accuracy, processor=None, store=False):

        # test accuracy in packets loss which is not more 1/number of %, e.g. 0.001 means 0.1%
        self.accuracy = accuracy
        # rate in-/decrease step
        self.step = step
        # number of maximum success attempts for calling rate valid
        self.max_succ = max_succ
        # test checking type
        self.check_type = check_type
        # key for rate parameters
        mode = firstfilter(lambda m: m.value == mode, TREXMODE)
        if mode == TREXMODE.stf:
            self.rate_key = RATEKEY.multiplier
        else:
            self.rate_key = RATEKEY.rate
        # number of succ attempts
        self.succ = 0
        # usefull for condition checking
        self.prev_rate = 0
        # data processor
        self.processor = processor
        # stores data for all tets attempt
        self.store = store
        self._first = True

    def __str__(self):
        return '<{}> accuracy: {}, step: {}, max_succ: {}, processor: {}, store: {}'.format(self.__class__.__name__, self.accuracy, self.step, self.max_succ, self.processor.__name__, self.store)

    def _raise(self, msg, err=None):
        raise SolverError(msg) from err

    def _raise_key_nf(self, key, err=None):
        self._raise('Wrong data format, key <{}> not found'.format(key), err=err)

    def _exception_handler(func):
        """decorator for handling common exceptions"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            template = partial('<{}> error occured during attempt {func} of {cls}'.format, func=func.__name__, cls=self.__class__.__name__)

            try:
                return func(self, *args, **kwargs)

            except KeyError as err:
                self._raise(template('Key'), err=err)

        return wrapper

    def _succ_incr(self):
        self.succ += 1

    @_exception_handler
    def _set_prev_rate(self, params):
        self.prev_rate = params[self.rate_key.value]

    def _succ_clean(self):
        self.succ = 0

    @_exception_handler
    def _rate_incr(self, params):
        # increases rate on rate increase step

        params[self.rate_key.value] += self.step
        return params

    @_exception_handler
    def _rate_decr(self, params):
        # decreases rate on rate increase step

        params[self.rate_key.value] -= self.step
        return params

    @_exception_handler
    def _set_rate(self, params, rate):
        # set rate with rate value

        params[self.rate_key.value] = rate
        return params

    def _extract_data(self, hub):
        # False and pop data from hub if no need in previous test data
        # otherwise stores data in hub

        try:
            return hub[-1] if self.store else hub.pop(0)

        except (IndexError, TypeError, SyntaxError) as err:
            raise SolverError('Something wrong with data hub', content=err.args)

    def _processed(self, data):
        # processes data with given processor

        try:
            return self.processor(data) if self.processor else data

        except ProcessorError as err:
            raise SolverError(err.message, **err.get_kwargs())

    @_exception_handler
    def _is_drop(self, data, key):

        for i in data:
            if int(i[key]) > 0:
                return True

        return False

    @_exception_handler
    def _is_loss(self, data):
        # finds losses in given data
        # TX - RX has to be less or equal accuracy (some % from TX)

        tx_p_0 = data['tx_ptks']['opackets-0']
        rx_p_1 = data['rx_ptks']['ipackets-1']
        tx_p_1 = data['tx_ptks']['opackets-1']
        rx_p_0 = data['rx_ptks']['ipackets-0']

        return int(tx_p_0 - rx_p_1) <= int(tx_p_0 * self.accuracy) and int(tx_p_1 - rx_p_0) <= int(tx_p_1 * self.accuracy)

    @_exception_handler
    def _eval_accuracy(self, data):

        return self._is_loss(data['global'])

    @_exception_handler
    def _eval_drop(self, data):

        for i in data['sampler']:
            if int(i['rx_drop_bps']) > (int(i['rx_bps']) * self.accuracy):
                return False

        return True

    def _eval_safe(self, data):

        return self._eval_drop(self, data) and self._eval_accuracy(self, data)

    def _get_indicator(self, data):
        # cheking result for different check types

        if self.check_type is CHECKTYPE.safe:
            indicator = self._eval_safe(data)
        elif self.check_type is CHECKTYPE.accuracy:
            indicator = self._eval_accuracy(data)
        elif self.check_type is CHECKTYPE.drop:
            indicator = self._eval_drop(data)
        else:
            self._raise('Seems somebody change check type on <{}>'.format(self.check_type))

        return indicator

    @_exception_handler
    def _fit_params(self, data, params):

        curr_rate = params[self.rate_key.value]
        indicator = self._get_indicator(data)

        # current rate more than previos and drops/losses are in within norm
        # rate increases
        if curr_rate > self.prev_rate and indicator:
            # set previos rate from given params
            self._set_prev_rate(params)
            # getting new params
            params = self._rate_incr(params)
            self._succ_clean()
        # current rate more than previos and drops/losses are out of norm
        # that means ceiling of rate was reached
        # rate has to be set to the same
        elif curr_rate > self.prev_rate and not indicator:
            params = self._set_rate(params, self.prev_rate)
            self._succ_clean()
        # current rate less than previos and drops/losses are in within of norm
        # that means floor of rate was reached
        # rate has to be set to the same
        # this is successful attempt
        elif curr_rate < self.prev_rate and indicator:
            self._succ_incr()
        # current rate less or equal than previos and drops/losses are out of norm
        # rate decreases
        elif curr_rate <= self.prev_rate and not indicator:
            # set previos rate from given params
            self._set_prev_rate(params)
            # getting new params
            params = self._rate_decr(params)
            self._succ_clean()
        # last test result approves selected rate
        # this is successful attempt
        else:
            self._succ_incr()

        return params

    @_exception_handler
    def _fit_first(self, data, params):

        # set previos rate from given params
        self._set_prev_rate(params)

        indicator = self._get_indicator(data)

        # if not losses
        if indicator:
            params = self._rate_incr(params)
        # if losses and drops
        else:
            params = self._rate_decr(params)

        return params

    def __call__(self, hub, params, *args, **kwargs):
        """general solver function

        checks if test result with certain rate is successful
        if not function changes test parameters in order to reach good result

        args:
            hub (list): list of processed by default processor tests result
            params (dict): params of latest test
            args: nothing

        kwargs: nothing

        return:
            (None): if success
            params (dict): if not success
        """
        # 1st test
        if self._first:
            self._first = False
            # set initial settings and return fitting parameters
            return self._fit_first(self._processed(self._extract_data(hub)), params)

        # test is done
        if self.succ >= self.max_succ:
            return None

        # return fitting parameters
        return self._fit_params(self._processed(self._extract_data(hub)), params)
