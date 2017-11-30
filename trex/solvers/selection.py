"""
solver tries to find suit test rate for given parameters

used simple logical model:
R is rate hase to be set
RS is rate step for in-/decrease rate
CR is current rate
PR is previos rate
D is drops/lossed occured in latest test (that is not within norm)

CR > PR and D is True --> R = R + RS
CR > PR and D is False --> R = PR
CR <= PR and D is True --> R = PR
CR <= PR and D is False --> R = R - RS
"""

from enum import Enum, unique
from functools import wraps, partial
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

    def __init__(self, accuracy=0.001, step=1, max_succ=3, rate_key=RATEKEY.multiplier, check_type=CHECKTYPE.accuracy, processor=None):

        # test accuracy in packets loss which is not more 1/number of %, e.g. 0.001 means 0.1%
        self.accuracy = accuracy
        # rate in-/decrease step
        self.step = step
        # number of maximum success attempts for calling rate valid
        self.max_succ = max_succ
        # test checking type
        self.check_type = check_type
        # key for rate parameters
        self.rate_key = rate_key
        # number of succ attempts
        self.succ = 0
        # usefull for condition checking
        self.prev_rate = 0
        # data processor
        self.processor = processor

    def _raise(self, msg):
        raise SolverError(msg)

    def _raise_key_nf(self, key):
        self._raise('Wrong data format, key <{}> not found'.format(key))

    def _exception_handler(func):
        """decorator for handling common exceptions"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            template = partial('{} error occured during attempt {reason}'.format, reason=func.__name__)

            try:
                return func(self, *args, **kwargs)

            except KeyError as err:
                self._raise(template('Key'))

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
            params = self._set_rate(params, self.prev_rate)
            self._succ_incr()
        # current rate less or equal than previos and drops/losses are out of norm
        # rate decreases
        elif curr_rate <= self.prev_rate and not indicator:
            params = self._rate_decr(params)
            self._succ_clean()
        # last test result approves selected rate
        # this is successful attempt
        else:
            self._succ_incr()

        return params

    @_exception_handler
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

        raise (SolverError): usually in case KeyError, but also in case other
        """

        # not enough data
        if len(hub) < 2:
            return params

        # no need previos test data only current
        hub.pop(0)

        # test is done
        if self.succ >= self.max_succ:
            return None

        # return fitting parameters
        return self._fit_params(self._processed(hub[-1]), params)
