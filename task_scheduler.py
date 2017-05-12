# work with DB
from app import db, models
# work with t-rex
from trex import test_proc
# for queueing
from rq import Queue
from rq.job import Job, cancel_job
from worker import redis_connect
# other
from datetime import datetime
import time
import json
# exception
from json import JSONDecodeError
# for correct stop
import signal
from sys import exit
from exceptions import GracefulExit, signal_handler


def task_finder():
    # searches appropriate tasks
    # dict of appropriate tasks
    appr_tasks = {}
    result = {'status': True, 'values': ''}
    # getting pending tasks
    tasks = models.Task.query.filter(models.Task.status == 'pending').order_by(models.Task.id).all()
    for task in tasks:
        # search for idle t-rexes and devices
        if task.trexes.status.lower() == 'idle' and task.devices.status.lower() == 'idle':
            # gathering dict appropriate tasks only one for t-rex and device pair ordered by creation time (lower task id)
            if not appr_tasks.get((task.trexes.id, task.devices.id), False):
                appr_tasks[(task.trexes.id, task.devices.id)] = task
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
        task.data = err_msg
        # defines task status
        task.status = 'done'

    while True:
        time.sleep(interval)
        print('task_queuer')
        tasks = task_finder()
        print(tasks)
        if tasks['status']:
            for task in tasks['values']:
                print('job added')
                # adding task to queue
                try:
                    # getting timeout
                    timeout = int(json.loads(task.tests.parameters)['trex']['duration']) + int(safe_int)
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
        # time.sleep(interval)


tasks_queue = Queue('tasks', connection=redis_connect, default_timeout=90)
statuses_queue = Queue('statuses', connection=redis_connect, default_timeout=30)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        task_queuer(interval=30)
    except (KeyboardInterrupt, GracefulExit):
        print('Got stop signal')
        working_task = models.Task.query.filter((models.Task.status == 'testing') | (models.Task.status == 'queued')).all()
        for task in working_task:
            job = Job.fetch(str(task.id), connection=redis_connect)
            if job.is_started or job.is_queued:
                cancel_job(str(job.get_id()), connection=redis_connect)
            task.status = 'pending'
            if task.trexes.status.lower() != 'idle':
                task.trexes.status = 'idle'
            if task.devices.status.lower() != 'idle':
                task.devices.status = 'idle'

        db.session.commit()
        print('DB sync done. Exiting...')
        exit()
