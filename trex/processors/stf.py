"""
returns dict of some trex data vaues
"""
from statistics import median_high
from ..exceptions import ProcessorError


def processor(data):
    """processes trex raw data CTRexResult obj and returns cleaned data

    args:
        data (CTRexResult): raw data from trex server

    return:
        success:
            (dict): certain part of given data:
                global (dict): global data values
                sampler (list): list of dicts, dict with certain trex values per data sample
                typical (dict): median of 'sampler'
        no data:
            (None)

    raise (ProcessorError): in case something wrong with data (AttributeError exception)
    """

    # if no data returns error
    try:
        if not len(data.get_value_list('.')):
            return None
    except (KeyError, AttributeError) as err:
        raise ProcessorError('Something wrong with data obj perhaps one is not CTRexResult or TRex API was changed', content=err.args)

    # keys for data samples
    sample_keys = {
        'tx_pps': 'trex-global.data.m_tx_pps',
        'rx_pps': 'trex-global.data.m_rx_pps',
        'tx_bps': 'trex-global.data.m_tx_bps',
        'rx_bps': 'trex-global.data.m_rx_bps',
        'rx_drop_bps': 'trex-global.data.m_rx_drop_bps',
        'queue_full': 'trex-global.data.m_total_queue_full',
        'queue_drop': 'trex-global.data.m_total_queue_drop'}
    # keys for global data
    global_keys = {
        'tx_ptks': ('trex-global.data', 'opackets-*'),
        'rx_ptks': ('trex-global.data', 'ipackets-*'),
        'tx_bytes': ('trex-global.data', 'obytes-*'),
        'rx_bytes': ('trex-global.data', 'ibytes-*')}

    """
    list of sampled data
    getting a dict with lists from raw data with sample_keys
    splits the dict to list of dicts with sample_keys
    1st and last samples are excluded due useless

    `data` --> ('a': [1, 2, 3]), ('b': [10, 20, 30]), ('c': [100, 200, 300]) -->
    [   {'a': 1, 'b': 10, 'c': 100},
        {'a': 2, 'b': 20, 'c': 200},
        {'a': 3, 'b': 30, 'c': 300}    ]

    """
    sampler_output = [{dk: dv[i] for dk, dv in zip(sample_keys.keys(), map(data.get_value_list, sample_keys.values()))} for i in range(1, (len(data.get_value_list('.')) - 1))]
    # general data
    global_data = {dk: data.get_last_value(*dv) for dk, dv in global_keys.items()}
    global_data['expected_pps'] = data.get_last_value('trex-global.data.m_tx_expected_pps')
    global_data['expected_bps'] = data.get_last_value('trex-global.data.m_tx_expected_bps')
    # making results
    return {
        'global': global_data,
        'sampler': sampler_output,
        # typical data from samples, its median
        'typical': sampler_output[median_high(range(1, (len(sampler_output))))]}
