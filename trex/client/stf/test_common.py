# common trex test processing
from . import trex_test_proc, trex_test_init, trex_reservation


def testing(**kwargs):
    # making initial checking
    trex_init = trex_test_init.initialize(**kwargs)
    if trex_init['state'] == 'ready':
        # trying to make a test
        result = trex_test_proc.test(**kwargs)
        # trying to cancel reservation after test, return nothing
        trex_reservation.cancel(**kwargs)
        # return result of testing
        return result
    # return error during init
    else:
        return trex_init
