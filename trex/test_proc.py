"""
* takes given task
* gather test settings from DB
* sets statuses of TRex and device
* sends one to [test_handler](#test_handler)
* receives data and writes one to DB
* restores statuses of TRex and device
"""

# DB
from app import db, models
# test processing
from . test_handler import test_handler
from datetime import datetime
from json import JSONDecodeError, dumps, loads
from checker import trex_check


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
        task.data = dumps({"error": '{0}'.format(result['state'])})
        # defines task status
        task.status = 'done'
        # defines result
        result['status'] = False
        # save data in DB
        db.session.commit()

    # template for test attributes
    test_attr = {}
    # trying to get test data parametrs from JSON
    try:
        test_attr['test_data'] = loads(task.test_data)
    except JSONDecodeError:
        result['state'] = 'import test data parameters error'
        task_err(result)
        return result
    # trying to define parametrs
    try:
        # defines task mode
        if test_attr['test_data'][0]['mode'] in {'stateful', 'stateless', 'bundle'}:
            test_attr['mode'] = test_attr['test_data'][0]['mode']
        else:
            task.start_time = datetime.now().replace(microsecond=0)
            result['state'] = 'task mode error'
            task_err(result)
            return result
        # defines test type
        if test_attr['test_data'][0]['test_type'] in {'common', 'selection', 'bundle'}:
            test_attr['type'] = test_attr['test_data'][0]['test_type']
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
        test_attr['params'] = loads(task.test_data)[0]['parameters']
    except JSONDecodeError:
        result['state'] = 'import test parameters error'
        task_err(result)
        return result

    # adds trex address and port
    # sets management entr from current DB mng entries by checking trex availability status
    trex_mng = trex_check(task.trexes)
    try:
        mng = trex_mng['mng']
    # trex is not available for all mng entries
    except KeyError:
        if trex_mng['state'] == 'unavailable':
            trex_mng['state'] = 'TRex is unavailable'
            task.trexes.status = 'down'
        elif trex_mng['state'] == 'No management data':
            trex_mng['state'] = 'No/Wrong TRex management data'
            task.trexes.status = 'error: "No/Wrong TRex management data"'
        task_err(trex_mng)
        return trex_mng

    # for single test writing trex mng and port into trex test params
    if test_attr['mode'] != 'bundle':
        test_attr['params']['trex']['trex_mng'] = mng
        # sets port
        test_attr['params']['trex']['daemon_port'] = task.trexes.port
    # for bundle just adding trex mng and port
    else:
        test_attr['params']['trex_mng'] = mng
        # sets port
        test_attr['params']['daemon_port'] = task.trexes.port

    # change statuses before test
    task.trexes.status = 'testing'
    # in case device is not empty
    if task.devices:
        task.devices.status = 'testing'
    task.status = 'testing'
    db.session.commit()

    # test processing
    result = test_handler(test_attr)

    # processing results
    # in case getting error
    if not result['status']:
        # possile error states for working TRex
        err_states = {
            'other_user',
            'duration is wrong',
            'trex option is wrong',
            'rate is equal or less than 0',
            'max count was exceeded',
            'unknown test mode',
            'unknown test type'}
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
    # in case device is not empty
    if task.devices:
        task.devices.status = 'idle'
    task.result = 'success'
    task.status = 'done'
    # type of result data depends on test type
    if test_attr['type'] == 'common':
        task.data = dumps({'trex': result['values']})
    elif test_attr['type'] == 'selection':
        task.data = dumps({'trex': result['values'], 'rate': result['rate']})
    else:
        task.data = dumps({'trex': result['values']})
    db.session.commit()
    # deletes test value from output
    result.pop('values', 'no values')
    return result
