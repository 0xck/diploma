import trex_test_proc
import trex_test_init
import trex_reservation


def testing(**kwargs):
    # making initial checking
    trex_init = trex_test_init.initialize(**kwargs)
    if trex_init['state'] == 'idle':
        # trying to make a test
        result = trex_test_proc.test(**kwargs)
        # trying to cancel reservation after test, return nothing
        trex_reservation.cancel(**kwargs)
        # return result of testing
        return result
    # return error during init
    else:
        return trex_init


if __name__ == '__main__':
    kwargs = dict(trex_mng='172.16.150.23', duration=35, warm=5, multiplier=100, sampler=10, daemon_port=8090)
    a = testing(**kwargs)
    print(a)
