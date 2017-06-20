from .trex_stf_lib.trex_client import CTRexClient
# exceptions
from .trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexIncompleteRunError
from jsonrpclib import ProtocolError


def force(trex_mng='127.0.0.1', daemon_port=8090, timeout=5, **kwargs):
    status = {'status': True, 'state': 'killed'}
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port, timeout=timeout)
    try:
        if not trex_connection.force_kill(confirm=False):
            status['status'] = False
            status['state'] = 'error force kill'
    except ProtocolError:
        status['status'] = False
        status['state'] = 'error kill rpc'
    return status


def soft(trex_mng='127.0.0.1', daemon_port=8090, timeout=5, **kwargs):
    status = {'status': True, 'state': 'killed'}
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port, timeout=timeout)
    try:
        if not trex_connection.stop_trex():
            status['status'] = False
            status['state'] = 'error soft kill'
    # other user already reserved trex
    except TRexRequestDenied:
        status['status'] = False
        status['state'] = 'other_user'
    # TRex process itself terminated with error fault or it has been terminated by an external intervention in the OS
    except TRexIncompleteRunError:
        status['status'] = False
        status['state'] = 'error fault during kill'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        status['status'] = False
        status['state'] = 'error kill rpc'
    return status
