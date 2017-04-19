from .trex_stf_lib.trex_client import CTRexClient
# exceptions
from jsonrpclib import ProtocolError


def check(trex_mng='127.0.0.1', daemon_port=8090, **kwargs):
    # return information about trex server status and availability
    # making connection
    trex_connection = CTRexClient(trex_host=trex_mng, trex_daemon_port=daemon_port)
    # trex daemon status info
    trex_status = {'status': True, 'state': 'idle'}
    # checking if trex demon is running
    # checking general connectivity
    try:
        # checking daemon connectivity
        if not trex_connection.check_server_connectivity():
            trex_status['status'] = False
            trex_status['state'] = 'unavailable'
            return trex_status
        # cheking is trex has active test
        if trex_connection.is_running():
            # has active test
            trex_status['state'] = 'running'
            return trex_status
        # checking if t-rex in stateless mode due some errors
        trex_cmd = trex_connection.get_trex_cmds()
        # checking for t-rex cmd args, trying to find "-i"
        for items in trex_cmd:
            for item in items:
                # trex in stateless mode due errors
                if ' -i ' in item:
                    trex_status['state'] = 'stateless'
    # checking general connectivity
    except ConnectionRefusedError:
        trex_status['status'] = False
        trex_status['state'] = 'unavailable'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        trex_status['status'] = False
        trex_status['state'] = 'error_rpc'
    return trex_status


if __name__ == "__main__":
    print(check())
