from . import trex_status, trex_reservation, trex_kill


def initialize(**kwargs):
    # makes checking and trying to make reservation
    # checking trex daemon status
    status = trex_status.check(**kwargs)
    # return error if trex is not available
    if not status['status']:
        return status
    # t-rex in stateless mode due error
    if status['state'] == 'stateless':
        # trying to kill
        trex_soft_kill = trex_kill.soft(**kwargs)
        if not trex_soft_kill['status']:
            # trying to force kill
            trex_force_kill = trex_kill.force(**kwargs)
            if not trex_force_kill['status']:
                return trex_force_kill
    # return error if trex is busy
    elif status['state'] != 'idle':
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
    # in case alright returns status True and state "ready"
    status['state'] = 'ready'
    return status
