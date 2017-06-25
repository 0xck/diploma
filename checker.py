# work with t-rex
from trex.client.stf import trex_status
# subprocess for ping
from subprocess import call, DEVNULL
# timeout
import timeout_decorator
# IPv6 support
from ipaddress import ip_address
from socket import gethostbyname
from socket import error as socket_error
from shutil import which
from os import X_OK
# for mng
from operator import itemgetter
from json import loads


def ping_checker(ip, num=3, timeout=0.5):
    # ping hosts by ip with 3 packets and 500ms interval by default
    try:
        # checking if IP
        ip_ver = ip_address(ip)
        # checking for IPv4/IPv6s, and ping util availability
        if ip_ver.version == 4:
            ping_util = which('ping', mode=X_OK)
        else:
            ping_util = which('ping6', mode=X_OK)
        # ping proccess
        if ping_util is not None:
            ping_check = call([ping_util, '-c', str(num), '-i', str(timeout), '-n', '-q', ip], stdout=DEVNULL)
        else:
            ping_check = 'ping util permission denied'
    # wrong IPv4/IPv6
    except ValueError:
        ping_check = 'ip error'
    return ping_check


def trex_check(trex, timeout=5):
    # checks trex condition; takes trex db entry as parameter

    @timeout_decorator.timeout(timeout, use_signals=False)
    def trex_checker(trex):
        # checks status with timeout
        result = False
        # sets management entr
        if trex.mng:
            mng = sorted(loads(trex.mng), key=itemgetter('priority'))
        # no mng info in DB
        else:
            result = dict(status=False, state='No management data')
            return result
        # trying to connect to trex using all mng items
        for mng_item in mng:
            # checking status in case items is not None
            if mng_item['mng']:
                try:
                    result = trex_status.check(trex_mng=mng_item['mng'], daemon_port=trex.port)
                    # in case first success
                    if result['status']:
                        result['mng'] = mng_item['mng']
                        break
                # in case unabling to resolve dns name
                except socket_error:
                    result = dict(status=False, state='unavailable')
        # all entries have None sa mng, that is wrong
        if not result:
            result = dict(status=False, state='No management data')
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
    result = False
    # sets management entr
    if device.mng:
        mng = sorted(loads(device.mng), key=itemgetter('priority'))
    # no mng info in DB
    else:
        result = dict(status=False, state='No management data')
        return result
    # trying to connect to trex using all mng items
    for mng_item in mng:
        # checking status in case items is not None
        if mng_item['mng']:
            if mng_item['type'] != 'fqdn':
                ping_check = ping_checker(mng_item['mng'])
            else:
                try:
                    ping_check = ping_checker(gethostbyname(mng_item['mng']))
                # in case unabling to resolve dns name
                except socket_error:
                    ping_check = 'DNS resolve error'
            # in case first success return "idle status"
            if ping_check == 0:
                result = dict(status=True, state='idle')
                return result
            elif ping_check in {'ip error', 'ping util permission denied', 'DNS resolve error'}:
                result = dict(status=False, state=ping_check)
            else:
                result = dict(status=False, state='unavailable')
    # all entries have None sa mng, that is wrong
    if not result:
        result = dict(status=False, state='No management data')
    return result
