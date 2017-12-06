"""
returns dict of some trex data vaues
"""
from statistics import median_high
from ..exceptions import ProcessorError


def processor(data, ifaces=[0, 1], slicer=None):
    """processes trex raw data list of dicts and returns cleaned data

    args:
        data (list): raw data from trex server

    return:
        success:
            (dict): certain part of given data:
                global (dict): global data values
                sampler (list): list of dicts, dict with certain trex values per data sample
                typical (dict): median of 'sampler'
        no data:
            (None)

    raise (ProcessorError): in case something wrong with data (IndexError, KeyError exceptions)
    """

    # if no data returns error
    try:
        data = data[slicer] if slicer else data

    except TypeError as err:
        raise ProcessorError('Something wrong with slicer: <{}>'.format(slicer), content=err.args)

    if not data:
        return None

    # keys for data samples
    sample_keys = [
        'tx_pps',
        'rx_pps',
        'tx_bps',
        'rx_bps',
        'rx_drop_bps',
        'queue_full',
        'queue_drop']
    # keys for global data
    global_keys = {
        'opackets': 'tx_ptks',
        'ipackets': 'rx_ptks',
        'obytes': 'tx_bytes',
        'ibytes': 'rx_bytes'}

    try:
        """
        list of sampled data
        raw data is a list of dicts
        extracts items (dicts) with sample_keys
        1st and last samples are excluded due useless and last contains global data

        [   {'g': {'a': 1, 'b': 2, 'c': 3}},
            {'g': {'a': 10, 'b': 20, 'c': 30}},
            {'g': {'a': 100, 'b': 200, 'c': 300}}   ] -->

        [   {'a': 1, 'b': 2, 'c': 3},
            {'a': 10, 'b': 20, 'c': 30},
            {'a': 100, 'b': 200, 'c': 300}  ] -->

        [   {'a': 1, 'c': 100},
            {'a': 2, 'c': 200},
            {'a': 3, 'c': 300}  ]

        """
        sampler_output = [{dk: dv for dk, dv in s.items() if dk in sample_keys} for s in (i['global'] for i in data)]

        """
        dict of global data
        getting port counters and adding them to new dict
        where old key of port is part of key with counter value

        {   'g': {'a': 1, 'b': 2, 'c': 3}},
            '0': {'a': 10, 'b': 20, 'c': 30}},
            '1': {'a': 100, 'b': 200, 'c': 300}}   }  -->

        {   'k':
            {'a-0': 10, 'a-1': 100},
            {'b-0': 20, 'b-1': 100} }
        """
        global_data = {global_keys[gk]: {'{}-{}'.format(gk, i): data[-1][i][gk] for i in ifaces} for gk in global_keys}
        # for compatibility with stateful
        global_data.update({'expected_pps': None, 'expected_bps': None})

    except (IndexError, KeyError) as err:
        raise ProcessorError('Something wrong with data', content=err.args)

    return {
        # general data
        'global': global_data,
        # sampled data
        'sampler': sampler_output,
        # typical data from samples, its median
        'typical': sampler_output[median_high(range(1, (len(sampler_output))))]}
