from . import trex_status, trex_reservation


def initialize(**kwargs):
    # makes checking and trying to makes test
    # checking trex daemon status
    # ! does not work with just open daemon port see https://trex-tgn.cisco.com/youtrack/issue/trex-404
    status = trex_status.check(**kwargs)
    # return error if trex is not available or busy
    if not status['status'] or status['state'] != 'idle':
        return status
    # trying to make reservation for current user
    reservation = trex_reservation.take(**kwargs)
    # in case trex already reserved tries to cancel reservation
    if not reservation['status']:
        cancel = trex_reservation.cancel(**kwargs)
        # return error if cancel was not successful
        if not cancel['status']:
            return cancel
        else:
            # trying to make reservation for current user after canceling
            reservation = trex_reservation.take(**kwargs)
            # retur error if rereservation was not successful
            if not reservation['status']:
                return reservation
    # in case alright return status True and state "idle"
    return status
