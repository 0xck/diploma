# takes tests, makes tests and returns result
# stateful tests
from trex.client.stf import test_common as stf_common
from trex.client.stf import test_selection as stf_selection
# statless tests
from trex.client.stl import test_common as stl_common
from trex.client.stl import test_selection as stl_selection
# for killing statefull
from trex.client.stf import trex_kill


def stf_test_common(**kwargs):
    # starts statefull common test with args for trex as kwargs
    # getting results
    result = stf_common.testing(**kwargs)
    return result


def stf_test_selection(**kwargs):
    # starts statefull selection test with args for trex as kwargs['trex'] and rate attr for Criterion class as kwargs['rate']
    # crating Criterion object for define test parametrs
    task = stf_selection.Criterion(**kwargs['rate'])
    # getting results
    result = stf_selection.testing(task, **kwargs['trex'])
    return result


def stl_test_common(**kwargs):
    # starts stateless common test with args for trex as kwargs
    # getting results
    result = stl_common.testing(**kwargs)
    # killing stateless mode
    #if trex_kill.soft(**kwargs):
    result['kill_status'] = True
    #else:
    #    result['kill_status'] = False
    return result


def stl_test_selection(**kwargs):
    # starts stateless selection test with args for trex as kwargs['trex'] and rate attr for Criterion class as kwargs['rate']
    # crating Criterion object for define test parametrs
    task = stl_selection.Criterion(**kwargs['rate'])
    # getting results
    result = stl_selection.testing(task, **kwargs['trex'])
    # killing stateless mode
    #if trex_kill.soft(**kwargs):
    result['kill_status'] = True
    #else:
    #    result['kill_status'] = False
    return result


def test_maker(test):
    # checking test type and provides proper test
    result = {'status': False, 'state': 'unknown test mode'}
    # statefull
    if test['mode'] == 'stateful':
        if test['type'] == 'common':
            result = stf_test_common(**test['params']['trex'])
        elif test['type'] == 'selection':
            result = stf_test_selection(**test['params'])
    # stateless
    else:
        if test['type'] == 'common':
            result = stl_test_common(**test['params']['trex'])
        elif test['type'] == 'selection':
            result = stl_test_selection(**test['params'])
    return result


def test_handler(test):
    # checking test type and prepares proper result form
    result = {'status': False, 'state': 'unknown test type'}
    # for single tests
    if test['type'] in {'common', 'selection'}:
        result = test_maker(test)
        # making result as list
        try:
            result['values'] = [result['values']]
        except KeyError:
            pass
    # for bundle
    elif test['type'] == 'bundle':
        test_result = []
        # making list with DB test entries
        test_list = [
            {
                # getting test entry from test data parameters of task
                'test': [test_data_item for test_data_item in test['test_data'][1:] if test_data_item['id'] == test_item['test_id']][0],
                # getting number of iteration
                'iter': test_item['iter']
            } for test_item in test['params']['bundle']]
        test_params = {}
        # for each test entry makes test
        for test_entr in test_list:
            # getting test params
            test_params['params'] = test_entr['test']['parameters']
            test_params['mode'] = test_entr['test']['mode']
            test_params['type'] = test_entr['test']['test_type']
            # adding trex and port
            test_params['params']['trex']['trex_mng'] = test['params']['trex_mng']
            test_params['params']['trex']['daemon_port'] = test['params']['daemon_port']
            # making tests per one for iteration
            for test_trying in range(test_entr['iter']):
                test_entr_result = test_maker(test_params)
                # handling errors
                if not test_entr_result['status']:
                    result['status'] = False
                    result['state'] = test_entr_result['state']
                    return result
                test_result.append(test_entr_result['values'])
        result['status'] = True
        result['state'] = 'success'
        result['values'] = test_result

    return result
