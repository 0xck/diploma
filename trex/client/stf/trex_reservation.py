from .trex_stf_lib.trex_client import CTRexClient
# exceptions
from .trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexInUseError
from jsonrpclib import ProtocolError


def take(trex_mng='127.0.0.1', daemon_port=8090, user=None, **kwargs):
    # takes reservation
    # making connection
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port)
    # trex taking reservation status info
    reservation_status = {'status': True, 'state': 'reserved'}
    # trying to take reservation
    try:
        if trex_connection.reserve_trex(user=user):
            # successfully took
            pass
    # other user already reserved trex
    except TRexRequestDenied:
        reservation_status['status'] = False
        reservation_status['state'] = 'other_user'
    # trex is alredy in use
    except TRexInUseError:
        reservation_status['status'] = False
        reservation_status['state'] = 'running'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        reservation_status['status'] = False
        reservation_status['state'] = 'error_rpc'
    return reservation_status


def check(trex_mng='127.0.0.1', daemon_port=8090, **kwargs):
    # chakes reservation
    # making connection
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port)
    # trex reservation status info
    reservation_status = {'status': True, 'state': 'reserved'}
    # trying to get status
    try:
        if trex_connection.is_reserved():
            return reservation_status
        else:
            reservation_status['status'] = False
            reservation_status['state'] = 'free'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        reservation_status['status'] = False
        reservation_status['state'] = 'error_rpc'
    return reservation_status


def cancel(trex_mng='127.0.0.1', daemon_port=8090, user=None, **kwargs):
    # cancels reservation
    # making connection
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port)
    # trex canceling reservation status info
    reservation_status = {'status': True, 'state': 'canceled'}
    # trying to cancel
    try:
        # successfully canceled
        if trex_connection.cancel_reservation(user=user):
            pass
        else:
            # reservation is already free
            reservation_status['state'] = 'free'
    # other user already reserved trex and the user is not the one trying to cancel the reservation
    except TRexRequestDenied:
        reservation_status['status'] = False
        reservation_status['state'] = 'other_user'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        reservation_status['status'] = False
        reservation_status['state'] = 'error_rpc'
    return reservation_status


'''
if __name__ == "__main__":
    print(take(trex_mng='172.16.150.23'))
'''
