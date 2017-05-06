from .trex_stl_lib.trex_stl_client import STLClient
from .trex_stl_lib.trex_stl_streams import STLProfile
import time
# exceptions
from .trex_stl_lib.trex_stl_exceptions import STLError, STLTimeoutError


def test(
    # server settings
    # trex daemon address
    trex_mng='127.0.0.1',
    # ports info
    sync_port=4501,
    async_port=4500,
    # user for trex operation
    # user='trex',
    # test pattern local file; only YAML now, cause need to figure out issue with py import, get class error there
    traffic_pattern='./trex/test/stl/udp_64b.yaml',
    # flow arguments
    # t-rex interfaces
    ifaces=[0, 1],
    # interface for active flow
    act_iface=0,
    # rate type PPS or BPS
    rate_type='pps',
    # number of pakets or bits
    rate=1000,
    # duration
    duration=60,
    # sampler for pseudo sampler, for making results same as stateful
    sampler=10,
    **kwargs
):

    def close_connection(client):
        # close connections in case failing
        result['status'] = False
        client.disconnect()

    result = {'status': True, 'state': ''}
    # getting streams from local file
    try:
        streams = STLProfile.load(traffic_pattern)
    except STLError:
        result['status'] = False
        result['state'] = 'error traffic pattern import'
        return result
    # making client connection
    client = STLClient(
        server=trex_mng,
        sync_port=sync_port,
        async_port=async_port)
    # connects to server
    try:
        client.connect()
    except STLError:
        result['status'] = False
        result['state'] = 'error connection'
        return result
    # acquires ports
    try:
        client.acquire(ports=ifaces)
    except STLError:
        result['state'] = 'error acquiring ports'
        client.disconnect()
        return result
    # test preparation
    # reset ports staistics
    try:
        client.reset(ports=ifaces)
    except STLError:
        result['state'] = 'error acquiring ports'
        close_connection(client)
        return result
    # makes ARP resolution in service mode
    try:
        client.set_service_mode(ports=act_iface, enabled=True)
    except STLError:
        result['state'] = 'error set service mode'
        close_connection(client)
        return result
    try:
        client.arp(ports=act_iface, retries=0)
    except STLError:
        result['state'] = 'error ARP resolving'
        close_connection(client)
        return result
    try:
        client.set_service_mode(ports=act_iface, enabled=False)
    except STLError:
        result['state'] = 'error unset service mode'
        close_connection(client)
        return result
    # adds streams to ports
    client.add_streams(streams, ports=act_iface)
    # clear the stats before injecting
    try:
        client.clear_stats()
    except STLError:
        result['state'] = 'error clearing stats'
        close_connection(client)
        return result
    # start test
    try:
        client.start(ports=act_iface, mult='{0}{1}'.format(rate, rate_type.lower()), duration=duration)
    except STLError:
        result['state'] = 'error start test'
        close_connection(client)
        return result
    # pseudo sampler for getting stats
    pseudo_sampler = []
    count = 0
    # getting stats for pseudo sampler exclude first and last
    while count < (duration / sampler - 1):
        time.sleep(sampler)
        test_result = client.get_stats(ports=ifaces, sync_now=True)
        data = {}
        data['tx_pps'] = test_result['global']['tx_pps']
        data['rx_pps'] = test_result['global']['rx_pps']
        data['tx_bps'] = test_result['global']['tx_bps']
        data['rx_bps'] = test_result['global']['rx_bps']
        data['rx_drop_bps'] = test_result['global']['rx_drop_bps']
        data['queue_full'] = test_result['global']['queue_full']
        # for compatibility with stateful
        data['queue_drop'] = 0
        pseudo_sampler.append(data)
        count += 1
    # block until done
    try:
        client.wait_on_traffic(ports=ifaces)
    except STLError:
        result['state'] = 'error traffic wait'
        close_connection(client)
        return result
    except STLTimeoutError:
        result['status'] = False
        result['state'] = 'error timeout'
        close_connection(client)
        return result
    # adds test result
    final_result = client.get_stats(ports=ifaces, sync_now=True)
    # types of rates
    rate_types_pkt = {'pps', 'kpps', 'mpps', 'gpps'}
    rate_types_bit = {'bps', 'kbps', 'mbps', 'gbps', 'tbps'}
    result['values'] = {
        # common data
        'global': {
            # for compatibility with stateful
            'tx_ptks': {'opackets-{}'.format(ifaces[iface]): final_result[iface]['opackets'] for iface in ifaces},
            'rx_ptks': {'ipackets-{}'.format(ifaces[iface]): final_result[iface]['ipackets'] for iface in ifaces},
            'tx_bytes': {'obytes-{}'.format(ifaces[iface]): final_result[iface]['obytes'] for iface in ifaces},
            'rx_bytes': {'ibytes-{}'.format(ifaces[iface]): final_result[iface]['ibytes'] for iface in ifaces},
            # choosing which "expected" will be included in result and which will be included as 0, for compatibility with stateful
            'expected_pps': rate if rate_type.lower() in rate_types_pkt else 0,
            'expected_bps': rate if rate_type.lower() in rate_types_bit else 0},
        # typical data from sample which is in third quarter of sampler's range
        'typical': pseudo_sampler[int((len(pseudo_sampler) * -0.25))],
        # sampled data from 2nd sampler and sampler before last
        'sampler': pseudo_sampler
    }
    # closing connection
    client.disconnect()
    return result
