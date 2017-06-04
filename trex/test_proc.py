from app import db, models
# stateful tests
from trex.client.stf import test_common as stf_common
from trex.client.stf import test_selection as stf_selection
# statless tests
from trex.client.stl import test_common as stl_common
from trex.client.stl import test_selection as stl_selection
from trex.client.stf import trex_kill
from datetime import datetime
import json
# exception
from json import JSONDecodeError


def test(task_id=0, **kwargs):
    # template for results
    result = {'status': True, 'state': '', 'task_id': task_id}
    # getting current task from DB
    task = models.Task.query.get(task_id)

    def task_err(result):
        # universal error func
        # defines end test time
        task.end_time = datetime.now().replace(microsecond=0)
        # defines test result
        task.result = 'error'
        # defines test data as error content
        task.data = json.dumps({"error": '{0}'.format(result['state'])})
        # defines task status
        task.status = 'done'
        # defines result
        result['status'] = False
        # save data in DB
        db.session.commit()

    # template for test attributes
    test_attr = {'mode': '', 'type': '', 'params': ''}
    # trying to define parametrs
    try:
        # defines task mode
        if task.tests.mode.lower() in {'stateful', 'stateless'}:
            test_attr['mode'] = task.tests.mode.lower()
        else:
            task.start_time = datetime.now().replace(microsecond=0)
            result['state'] = 'task mode error'
            task_err(result)
            return result
        # defines test type
        if task.tests.test_type.lower() in {'common', 'selection'}:
            test_attr['type'] = task.tests.test_type.lower()
        else:
            task.start_time = datetime.now().replace(microsecond=0)
            result['state'] = 'test type error'
            task_err(result)
            return result
    # in case there is not the task with the id
    except KeyError:
        result['status'] = False
        result['state'] = 'task id error'
        return result
    # cheking current trex and device status
    # set start time
    task.start_time = datetime.now().replace(microsecond=0)
    # checking trex status
    try:
        # trex is not busy or down etc
        if task.trexes.status.lower() != 'idle':
            result['state'] = 'trex is not idle'
            task_err(result)
            return result
        # in case device is not empty
        if task.devices:
            # device is not busy or down etc
            if task.devices.status.lower() != 'idle':
                result['state'] = 'device is not idle'
                task_err(result)
                return result
    # something wrong with trex or device name
    except AttributeError:
        result['state'] = 'trex or device name error'
        task_err(result)
        return result
    # trying to get test parametrs from JSON
    try:
        test_attr['params'] = json.loads(task.tests.parameters)
    except JSONDecodeError:
        result['state'] = 'import test parameters error'
        task_err(result)
        return result

    # adds trex address and port
    # sets management entr
    if task.trexes.ip4:
        mng = task.trexes.ip4
    elif task.trexes.ip6:
        mng = task.trexes.ip6
    elif task.trexes.fqdn:
        mng = task.trexes.fqdn
    test_attr['params']['trex']['trex_mng'] = mng
    # sets port
    test_attr['params']['trex']['daemon_port'] = task.trexes.port

    # change statuses before test
    task.trexes.status = 'testing'
    # in case device is not empty
    if task.devices:
        task.devices.status = 'testing'
    task.status = 'testing'
    db.session.commit()

    # test processing
    if test_attr['mode'] == 'stateful':
        if test_attr['type'] == 'common':
            result = stf_test_common(**test_attr['params']['trex'])
        elif test_attr['type'] == 'selection':
            result = stf_test_selection(**test_attr['params'])
    else:
        if test_attr['type'] == 'common':
            result = stl_test_common(**test_attr['params']['trex'])
        elif test_attr['type'] == 'selection':
            result = stl_test_selection(**test_attr['params'])

    # processing results
    # in case getting error
    if not result['status']:
        # possile error states for working TRex
        err_states = {
            'other_user',
            'duration is wrong',
            'trex option is wrong',
            'rate is equal or less than 0',
            'max count was exceeded'}
        kill_err = {
            'error force kill',
            'error kill rpc',
            'error soft kill',
            'error fault during kill'
        }
        # checking for reservation and TRex parameter errors
        if result['state'] in err_states:
            task.trexes.status = 'idle'
        # in case TRex was in stateless due error and trying to resolve was unsuccessful
        elif result['state'] in kill_err:
            task.trexes.status = 'error'
        # for something wrong with TRex
        else:
            task.trexes.status = result['state']
        # return error
        # in case device is not empty
        if task.devices:
            task.devices.status = 'idle'
        result['task_id'] = task_id
        task_err(result)
        return result
    # in case test is done
    # set test end time
    task.end_time = datetime.now().replace(microsecond=0)
    # change statuses
    task.trexes.status = 'idle'
    # cheking kill status after stateless test
    if test_attr['mode'] == 'stateless':
        if not result['kill_status']:
            task.trexes.status = 'error'
    # in case device is not empty
    if task.devices:
        task.devices.status = 'idle'
    task.result = 'success'
    task.status = 'done'
    # type of result data depends on test type
    if test_attr['type'] == 'common':
        task.data = json.dumps({'trex': result['values']})
    else:
        task.data = json.dumps({'trex': result['values'], 'rate': result['rate']})
    db.session.commit()
    # will add later
    # result.pop('values')
    return result


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
    if trex_kill.soft(**kwargs):
        result['kill_status'] = True
    else:
        result['kill_status'] = False
    return result


def stl_test_selection(**kwargs):
    # starts stateless selection test with args for trex as kwargs['trex'] and rate attr for Criterion class as kwargs['rate']
    # crating Criterion object for define test parametrs
    task = stl_selection.Criterion(**kwargs['rate'])
    # getting results
    result = stl_selection.testing(task, **kwargs['trex'])
    # killing stateless mode
    if trex_kill.soft(**kwargs):
        result['kill_status'] = True
    else:
        result['kill_status'] = False
    return result
