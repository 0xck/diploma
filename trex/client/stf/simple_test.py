import stateful_proc
import trex_status
import trex_reservation


def processing(**kwargs):
    # makes checking and trying to makes test
    # args for checking func
    trex_mng = kwargs['trex_mng']
    daemon_port = kwargs['daemon_port']
    # checking trex daemon status
    # ! does not work with just open daemon port see https://trex-tgn.cisco.com/youtrack/issue/trex-404
    status = trex_status.check(trex_mng=trex_mng, daemon_port=daemon_port)
    # return error if trex is not available or busy
    if not status['status'] or status['state'] != 'idle':
        return status
    # trying to make reservation for current user
    reservation = trex_reservation.take(trex_mng=trex_mng, daemon_port=daemon_port)
    # in case trex already reserved tries to cancel reservation
    if not reservation['status']:
        cancel = trex_reservation.cancel(trex_mng=trex_mng, daemon_port=daemon_port)
        # return error if cancel was not successful
        if not cancel['status']:
            return cancel
        else:
            # trying to make reservation for current user after canceling
            reservation = trex_reservation.take(trex_mng=trex_mng, daemon_port=daemon_port)
            # retur error if rereservation was not successful
            if not reservation['status']:
                return reservation
    # trying to make a test
    result = stateful_proc.test(**kwargs)
    # return error in case any issues with trex during testing
    if not result['status']:
        return result
    # trying to cancel reservation after test, return nothing
    trex_reservation.cancel(trex_mng=trex_mng, daemon_port=daemon_port)
    return result


if __name__ == '__main__':
    kwargs = dict(trex_mng='172.16.150.23', duration=35, warm=5, multiplier=100, sampler=10, daemon_port=8090)
    a = processing(**kwargs)
    print(a)
