# stateful trex test init cause it has all necessary for init
from .. stf import trex_test_init
# stateful client
from .. stf.trex_stf_lib.trex_client import CTRexClient
# exceptions
from .. stf.trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexInUseError, TRexError
from jsonrpclib import ProtocolError


def start_stateless(trex_mng='127.0.0.1', daemon_port=8090, hw_chsum=False, timeout=5, **kwargs):
    # trying to enable stateless mode
    status = {'status': True, 'state': 'ready'}
    try:
        stl_init = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port, timeout=timeout)
        # stateless start fail
        if not stl_init.start_stateless(checksum_offload=hw_chsum):
            status['status'] = False
            status['state'] = 'error with stateless start'
    # the trex option raised an exception at server
    except TRexError:
        status['status'] = False
        status['state'] = 'trex option is wrong'
    # trex is alredy in use
    except TRexInUseError:
        status['status'] = False
        status['state'] = 'running'
    # other user already reserved trex
    except TRexRequestDenied:
        status['status'] = False
        status['state'] = 'other_user'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        status['status'] = False
        status['state'] = 'error_rpc'
    return status


def initialize(**kwargs):
    # checking status and initializing t-rex
    # getting t-rex daemon status with stateful client
    status = trex_test_init.initialize(**kwargs)
    # in case t-rex is ready to take connection
    if status['state'] == 'ready':
        status = start_stateless(**kwargs)
    # in case alright returns status True and state "ready", in any other case returns False and error as state
    elif status['state'] == 'stateless':
        status['state'] == 'ready'
    return status
