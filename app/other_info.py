general_notes = {
    'table_req': 'All fields above are required',
}

stf_traffic_patterns = [
    'cap2/dns.yaml',
    'cap2/dns_one_server.yaml',
    'cap2/http_simple.yaml',
    'cap2/http_short.yaml',
    'cap2/http_very_long.yaml',
    'cap2/http.yaml',
    'cap2/imix_1518.yaml',
    'cap2/imix_64_100k.yaml',
    'cap2/imix_64_fast.yaml',
    'cap2/imix_64.yaml',
    'cap2/imix_9k.yaml',
    'cap2/imix_fast_1g_100k_flows.yaml',
    'cap2/imix_fast_1g.yaml',
    'cap2/imix.yaml',
    'cap2/ipv4_load_balance.yaml',
    'cap2/rtsp.yaml',
    'cap2/sfr2.yaml',
    'cap2/sfr3.yaml',
    'cap2/sfr.yaml',
    'cap2/short_tcp.yaml',
    'cap2/sip_short1.yaml',
    'cap2/sip_short2.yaml',
]
stf_notes = {
    'test': [
        'Common is simple test which executes one time',
        'Selection is test which executes different number of time in order to reach result defined in parameters'
    ],
    'pattern': ['Test pattern which executes on T-rex (for some reason pattern must located on T-rex now)'],
    'multiplier': ['Multiplier affects test pattern values (number of packets per second and packet flow gaps)'],
    'sampler': ['Sampler defines intervals for gathering and saving statistic during test. Every sampler interval statistic writes and in future one will be showed on chart (for some reason number of sampler size limited to 100 entries now, be careful choose appropriate value)'],
    'warm': ['Time for "warm" traffic which services for reasons like in case need to wait for some changes on network like tunnel upping, STP/dot1X timeouts, etc (migth not work on VM due some T-rex soft nuances in current releases)'],
}
