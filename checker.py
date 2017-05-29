# work with t-rex
from trex.client.stf import trex_status
# subprocess for ping
from subprocess import call, DEVNULL
# timeout
import timeout_decorator


def trex_check(trex):
    # checks trex condition; takes trex db entry as parameter

    @timeout_decorator.timeout(timeout=10, use_signals=False)
    def trex_checker(trex):
        # checks status with timeout
        result = trex_status.check(trex_mng=trex.ip4, daemon_port=trex.port)
        return result

    # getting result
    try:
        result = trex_checker(trex)
    # timeout
    except timeout_decorator.timeout_decorator.TimeoutError:
        result = dict(status=False, state='unavailable')
    return result


def device_check(device):
    # checks device condition; takes device db entry as parameter
    ping_check = call(['ping', '-c', '3', '-n', device.ip4], stdout=DEVNULL)
    if ping_check == 0:
        result = dict(status=True, state='idle')
    else:
        result = dict(status=False, state='unavailable')
    return result


if __name__ == '__main__':
    result = trex_status.check(trex_mng='192.168.0.192', daemon_port=8090)
    print(result)
