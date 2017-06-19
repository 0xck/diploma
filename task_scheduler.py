# task scheduller for handling pending tasks and makes test with trex client
# work with DB
from app import db, models
# work with TRex
from trex import test_proc
# for queueing
from rq import Queue, get_failed_queue
from rq.job import Job, cancel_job
from worker import redis_connect
# other
from datetime import datetime
from time import sleep
# exception
from json import JSONDecodeError, loads, dumps
# for correct stop
import signal
from sys import exit
from exceptions import GracefulExit, signal_handler
from trex.client.stf import trex_kill
# task scheduller config
from config import task_sched_interval, task_sched_safe


def task_finder():
    # searches appropriate tasks
    # dict of appropriate tasks
    appr_tasks = {}
    result = {'status': True}
    # getting pending tasks
    tasks = models.Task.query.filter(models.Task.status == 'pending').order_by(models.Task.id).all()
    for task in tasks:
        # search for idle TRexes and devices
        # if devise is not empty
        if task.devices:
            if task.trexes.status.lower() == 'idle' and task.devices.status.lower() == 'idle':
                # gathering dict appropriate tasks only one for TRex and device pair ordered by creation time (lower task id)
                if not appr_tasks.get((task.trexes.id, task.devices.id), False):
                    appr_tasks[(task.trexes.id, task.devices.id)] = task
        else:
            if task.trexes.status.lower() == 'idle':
                # gathering dict appropriate tasks only one for TRex ordered by creation time (lower task id)
                if not appr_tasks.get((task.trexes.id, None), False):
                    appr_tasks[(task.trexes.id, None)] = task
    # making list of tasks in case of they exist
    if len(appr_tasks) > 0:
        result['values'] = [appr_tasks[task] for task in appr_tasks]
    else:
        result['status'] = False
        result['state'] = 'no appropriate tasks'
    return result


def task_queuer(interval=300, safe_int=600):
    # checking DB for appropriate tasks in cycle

    def err_handler(task, err_msg):
        # parameter error handler
        # inserting task time etc
        task_time = datetime.now().replace(microsecond=0)
        task.start_time = task_time
        task.end_time = task_time
        task.result = 'error'
        # defines test data as error content
        task.data = dumps({'error': err_msg})
        # defines task status
        task.status = 'done'

    while True:
        sleep(interval)
        tasks = task_finder()
        if tasks['status']:
            for task in tasks['values']:
                test_data = loads(task.test_data)[0]
                # adding task to queue
                try:
                    # getting timeout; in case selection timeout is summ of max attempt * duration + safe value
                    if test_data['mode'] != 'bundle':
                        timeout = (test_data['parameters']['trex']['duration'] * 1 if test_data['test_type'] != 'selection' else test_data['parameters']['rate']['max_test_count']) + safe_int
                    else:
                        timeout = safe_int
                        # making timeout as summ of all tests timeouts
                        test_params = test_data['parameters']['bundle']
                        for test_entr in test_params:
                            # getting test params
                            test = [test_data_item for test_data_item in test_data if test_data_item['id'] == test_entr['test_id']][0]
                            timeout += (test['parameters']['trex']['duration'] * 1 if test['test_type'] != 'selection' else test['parameters']['rate']['max_test_count']) * test_entr['iter']
                    # adding task to queue
                    tasks_queue.enqueue_call(func=test_proc.test, kwargs={'task_id': task.id}, job_id=str(task.id), result_ttl=0, timeout=timeout)
                    # updating task status
                    task.status = 'queued'
                # in case load parameters error set task status as error and is not queued one
                except JSONDecodeError:
                    err_handler(task, 'import test parameters error')
                except ValueError:
                    err_handler(task, 'error duration parameters')
                except KeyError:
                    err_handler(task, 'no duration parameters')
                # commit DB changes
                db.session.commit()


# creating task queue
tasks_queue = Queue('tasks', connection=redis_connect, default_timeout=90)


def task_killer(task):
    # kills task and executing trex task; getting db item as task
    job = Job.fetch(str(task.id), connection=redis_connect)
    # deleting current task from queue
    if job.is_started or job.is_queued:
        cancel_job(str(job.get_id()), connection=redis_connect)
    # kills executing trex task
    result = {'status': False, 'state': ''}
    # sets management entr
    if task.trexes.ip4:
        mng = task.trexes.ip4
    elif task.trexes.ip6:
        mng = task.trexes.ip6
    elif task.trexes.fqdn:
        mng = task.trexes.fqdn
    # trying soft kill
    soft_kill = trex_kill.soft(trex_mng=mng, daemon_port=task.trexes.port)
    force_kill = {'status': False}
    # trying force kill
    if not soft_kill['status']:
        force_kill = trex_kill.force(trex_mng=mng, daemon_port=task.trexes.port)
    # if kill was succesful makes DB changes
    if soft_kill['status'] or force_kill['status']:
        result['status'] = True
        # making DB changes
        task.status = 'canceled'
        if task.trexes.status.lower() != 'idle':
            task.trexes.status = 'idle'
        # in case device is not empty
        if task.devices:
            if task.devices.status.lower() != 'idle':
                task.devices.status = 'idle'
        db.session.commit()
    # if kill was not succesful returns error msg
    else:
        result['state'] = 'soft kill: {}, force kill: {}'.format(soft_kill['state'], force_kill['state'])
    return result


if __name__ == '__main__':
    # for correct stopping
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        task_queuer(interval=task_sched_interval, safe_int=task_sched_safe)
    except (KeyboardInterrupt, GracefulExit):
        print('Got stop signal')
        # finds all testing tasks and sets their status to pending
        working_task = models.Task.query.filter((models.Task.status == 'testing') | (models.Task.status == 'queued')).all()
        # if tasks were found delete them from queue and kill executing trex
        if len(working_task) > 0:
            for task in working_task:
                job = Job.fetch(str(task.id), connection=redis_connect)
                # deleting current queued task
                if job.is_started or job.is_queued:
                    cancel_job(str(job.get_id()), connection=redis_connect)
                # kills executing trex task
                # sets management entr
                if task.trexes.ip4:
                    mng = task.trexes.ip4
                elif task.trexes.ip6:
                    mng = task.trexes.ip6
                elif task.trexes.fqdn:
                    mng = task.trexes.fqdn
                if not trex_kill.soft(trex_mng=mng, daemon_port=task.trexes.port)['status']:
                    trex_kill.force(trex_mng=mng, daemon_port=task.trexes.port)
                # making DB changes
                task.status = 'pending'
                if task.trexes.status.lower() != 'idle':
                    task.trexes.status = 'idle'
                # in case device is not empty
                if task.devices:
                    if task.devices.status.lower() != 'idle':
                        task.devices.status = 'idle'
        # clear failed queues
        failed_task = get_failed_queue(connection=redis_connect)
        if failed_task.count > 0:
            failed_task.empty()
        # writing changes to DB
        db.session.commit()
        print('DB syncing is done. Exiting...')
        exit()
