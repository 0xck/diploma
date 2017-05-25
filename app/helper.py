def humanize(data, units='si', end=''):
    types = ('', '', 'K', 'M', 'G', 'P', 'E')
    if units == 'si':
        base = 1000
    else:
        base = 1024
    if data > base:
        for i in range(2, 6):
            if data < base ** i:
                return '{:.2f}{}{}'.format(data / (base ** (i - 1)), types[i], end)
                break
    else:
        return str(data) + ' ' + end


general_notes = {
    'table_req': 'All fields above are required',
}

test_types = ['common', 'selection']  # in future 'cyclic', 'bundle'

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
        '"Common" is simple test which executes one time',
        '"Selection" is test which executes different number of time in order to reach result defined in parameters'
    ],
    'pattern': ['Test pattern which is executed on T-rex (for some reason pattern must located on T-rex now)'],
    'multiplier': ['Multiplier affects test pattern values (number of packets per second and packet flow gaps)'],
    'sampler': ['Sampler defines intervals for gathering and saving statistic during test. Every sampler interval statistic writes and in future one will be showed on chart (for some reason number of sampler size limited to 100 entries now, be careful choose appropriate value)'],
    'warm': ['Time for "warm" traffic which services for reasons like in case need to wait for some changes on network like tunnel upping, STP/dot1X timeouts, etc (migth not work on VM due some T-rex soft nuances in current releases)'],
    'accuracy': ['Accuracy defines percent of per flow packet loss which can be accepted for passing test'],
    'rate_incr_step': ['Rate step value will be used for increasing/decreasing rate value in case test pass/not pass'],
    'selection_test_type': [
        'Defines which value will be used for checking test passing:',
        '"Safe" considers computed losses and t-rex queue drop (strictest requirement for losses checking)',
        '"Accuracy" considers computed losses only (strict requirement for losses checking)',
        '"Drop" considers t-rex queue drop/overload only (less strict requirement for losses checking)'
    ]
}

stl_notes = {
    'test': stf_notes['test'],
    'pattern': ['Test pattern which is executed on T-rex'],
    'rate': ['Number of packets or bits per second'],
    'rate_type': ['Value for rate defines pps or bps rate will be used in test'],
    'sampler': stf_notes['sampler'],
    'accuracy': stf_notes['accuracy'],
    'rate_incr_step': stf_notes['rate_incr_step'],
    'selection_test_type': stf_notes['selection_test_type'],
}

stl_test_val = {
    'rate_types': ['pps', 'bps']
}

sel_test_types = {
    'all': ['safe', 'accuracy', 'drop']
}

validator_err = {
    'exist': 'Item already exists. For adding, change its value, please.'
}

tasks_statuses = {
    'all': ['done', 'pending', 'hold', 'testing', 'canceled'],
    'gui_new': ['pending', 'hold'],
    'gui_edit': ['pending', 'hold', 'canceled']
}

trexes_statuses = {
    'all': ['idle', 'down', 'testing', 'error'],
    'gui': ['idle', 'down'],
}

devices_statuses = {
    'all': trexes_statuses['all'],
    'gui': trexes_statuses['gui'],
}

messages = {
    'success': '''
        <div class="alert alert-success alert-dismissible" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <strong>Success!</strong> {}
        </div>''',
    'no_succ': '''
        <div class="alert alert-danger alert-dismissible" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <strong>Fail!</strong> {}
        </div>''',
    'succ_no_close': '<div class="alert alert-success" role="alert"><strong>Success!</strong> {}</div>',
    'no_succ_no_close': '<div class="alert alert-danger" role="alert"><strong>Success!</strong> {}</div>',
    'warn_no_close': '<div class="alert alert-warinig" role="alert"><strong>Success!</strong> {}</div>',
}
