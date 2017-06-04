# work with t-rex
from trex.client.stf import trex_status
# subprocess for ping
from subprocess import call, DEVNULL
# timeout
import timeout_decorator


def trex_check(trex, timeout=5):
    # checks trex condition; takes trex db entry as parameter

    @timeout_decorator.timeout(timeout, use_signals=False)
    def trex_checker(trex):
        # checks status with timeout
        # sets management entr
        if trex.ip4:
            mng = trex.ip4
        elif trex.ip6:
            mng = trex.ip6
        elif trex.fqdn:
            mng = trex.fqdn
        result = trex_status.check(trex_mng=mng, daemon_port=trex.port)
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
    # 3 packets with 500ms interval
    # sets management entr
    if device.ip4:
        mng = device.ip4
    elif device.ip6:
        mng = device.ip6
    elif device.fqdn:
        mng = device.fqdn
    ping_check = call(['ping', '-c', '3', '-i', '0.5', '-n', '-q', mng], stdout=DEVNULL)
    if ping_check == 0:
        result = dict(status=True, state='idle')
    else:
        result = dict(status=False, state='unavailable')
    return result
