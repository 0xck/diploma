from .trex_stf_lib.trex_client import CTRexClient
# exceptions
from .trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexInUseError, TRexError
from jsonrpclib import ProtocolError


def test(
    # server settings
    # trex daemon address
    trex_mng='127.0.0.1',
    # trex local config file
    conf='/etc/trex_cfg.yaml',
    # test duration
    duration=60,
    # multiplier
    multiplier=1,
    # test pattern local file
    traffic_pattern='cap2/dns.yaml',
    # latency checking packet number, if 0 latency test is disabled
    latency_num=0,
    # traffic warm up time
    warm=10,
    # work as software appliance
    soft_test=True,
    # timeout before init interfacesand send traffic
    wait=1,
    # IPv6 support
    ipv6_enable=False,
    # HW checksumm offloading
    hw_chsum=False,
    # only latency test disable
    latency_enable=False,
    # trex daemon port
    daemon_port=8090,
    # client settings
    # max history size
    history_size=100,
    # history sampler
    sampler=1,
    # timeout
    timeout=5
):
    # result of test trying
    result = {'status': True, 'values': ''}
    # trying to make a test
    try:
        # making connection
        trex_connection = CTRexClient(
            trex_host=trex_mng,
            max_history_size=history_size,
            trex_daemon_port=daemon_port)
        # starting test proccess
        trex_connection.start_trex(
            cfg=conf,
            d=duration,
            m=multiplier,
            f=traffic_pattern,
            l=latency_num,
            k=warm,
            software=soft_test,
            w=wait,
            ipv6=ipv6_enable,
            checksum_offload=hw_chsum,
            lo=latency_enable,
            timeout=timeout)
        # getting test result
        test_result = trex_connection.sample_to_run_finish(time_between_samples=sampler)
        # list for sampled data
        sampler_output = []
        # gathering info from samples
        for i in range(1, (len(test_result.get_value_list('.')) - 1)):
            data = {
                'tx_pps': test_result.get_value_list('trex-global.data.m_tx_pps')[i],
                'rx_pps': test_result.get_value_list('trex-global.data.m_rx_pps')[i],
                'tx_bps': test_result.get_value_list('trex-global.data.m_tx_bps')[i],
                'rx_bps': test_result.get_value_list('trex-global.data.m_rx_bps')[i],
                'rx_drop_bps': test_result.get_value_list('trex-global.data.m_rx_drop_bps')[i],
                'queue_full': test_result.get_value_list('trex-global.data.m_total_queue_full')[i],
                'queue_drop': test_result.get_value_list('trex-global.data.m_total_queue_drop')[i]}
            sampler_output.append(data)
        # making results
        result['values'] = {
            # common data
            'global': {
                'tx_ptks': test_result.get_last_value('trex-global.data', 'opackets-*'),
                'rx_ptks': test_result.get_last_value('trex-global.data', 'ipackets-*'),
                'tx_bytes': test_result.get_last_value('trex-global.data', 'obytes-*'),
                'rx_bytes': test_result.get_last_value('trex-global.data', 'ibytes-*'),
                'expected_pps': test_result.get_last_value('trex-global.data.m_tx_expected_pps'),
                'expected_bps': test_result.get_last_value('trex-global.data.m_tx_expected_bps')
            },
            # typical data from sample which is in third quarter of sampler's range
            'typical': sampler_output[int(len(test_result.get_value_list('.')) * -0.25)],
            # sampled data from 2nd and slice before last
            'sampler': sampler_output,
            # duration for correct task data info showing
            'duration': duration
        }
    # "d" parameter inserted with wrong value one must be at least 30 seconds long
    except ValueError:
        result['status'] = False
        result['state'] = 'duration is wrong'
    # the trex option raised an exception at server
    except TRexError:
        result['status'] = False
        result['state'] = 'trex option is wrong'
    # trex is alredy in use
    except TRexInUseError:
        result['status'] = False
        result['state'] = 'running'
    # other user already reserved trex
    except TRexRequestDenied:
        result['status'] = False
        result['state'] = 'other_user'
    # JSON-RPC erros, something is wrong with code or server
    except ProtocolError:
        result['status'] = False
        result['state'] = 'error_rpc'
    return result



if __name__ == '__main__':
    a = test(trex_mng='172.16.150.23', duration=65, warm=5, multiplier=100, sampler=10)
    print(a)
