# t-rex model page
from flask import render_template, abort
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import Required, Length, AnyOf
from json import loads
from bitmath import *


@app.route('/tasks/')
def tasks():
    tasks_entr = models.Task.query.order_by(models.Task.id.desc()).all()
    table_data = ''
    act_button_template = {
        'begin': '''<div class="btn-group">
                        <button type="button" class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">''',
        'end': '''<li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
                </ul>
            </div>''',
        'separator': '<li role="separator" class="divider"></li>',
        'hold': '<li><a href="/task/{0}/hold" class="hold" id="{0}">On hold</a></li>',
        'queue': '<li><a href="/task/{0}/queue" class="queue" id="{0}">To queue</a></li>',
        'readd': '<li><a href="/task/{0}/readd" class="readd" id="{0}">Re add</a></li>',
        'cancel': '<li><a href="/task/{0}/cancel" class="cancel" id="{0}">Cancel</a></li>'
    }

    for entr in tasks_entr:
        if entr.result == 'success':
            status_row = 'tr class="success"'
        elif entr.result == 'error':
            status_row = 'tr class="danger"'
        else:
            status_row = 'tr'
        act_button = act_button_template['begin']
        if entr.status == 'pending':
            act_button += act_button_template['hold'] + act_button_template['separator'] + act_button_template['cancel'] + act_button_template['end']
        elif entr.status == 'done':
            act_button += act_button_template['readd'] + act_button_template['end']
        elif entr.status == 'hold':
            act_button += act_button_template['queue'] + act_button_template['separator'] + act_button_template['cancel'] + act_button_template['end']
            status_row = 'tr class="info"'
        elif entr.status == 'canceled':
            act_button += act_button_template['readd'] + act_button_template['end']
            status_row = 'tr class="active"'
        else:
            act_button += act_button_template['hold'] + act_button_template['queue'] + act_button_template['separator'] + act_button_template['readd'] + act_button_template['cancel'] + act_button_template['end']
        table_data += '''
            <{5}>
                <td>{id}</td>
                <td class="task_status {5}">{status}</td>
                <td>{result}</td>
                <td>{description}</td>
                <td>{start_time}</td>
                <td>{end_time}</td>
                <td>{3}</td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{4}</td>
                <td>{0}</td>

            </tr>
                '''.format(
                        ('<a href="/task/{0}">Show</a>'.format(entr.id) if entr.status.lower() in {'done', 'error'} else 'Is not collected yet'),
                        ('<a href="/trex/{1}">{0}</a>'.format(entr.trexes.hostname, entr.trexes.id)),
                        ('<a href="/device/{1}">{0}</a>'.format(entr.devices.name, entr.devices.id)),
                        ('<a href="/test/{1}">{0}</a>'.format(entr.tests.name, entr.tests.id)),
                        act_button.format(entr.id),
                        status_row,
                        **entr['ALL_DICT'])

    return render_template(
        'tasks.html',
        title='List of tasks',
        content=table_data,
        script_file='tasks.js')


@app.route('/task/new/', methods=['GET', 'POST'])
def task_create():
    # get tests list
    get_tests = models.Test.query.order_by(models.Test.id.desc()).all()
    tests = [test.name for test in get_tests]
    list_tests = ([(test, test) for test in tests[1:]])
    list_tests.insert(0, (tests[0], '{} (Default)'.format(tests[0])))
    # get trexes list
    get_trexes = models.Trex.query.order_by(models.Trex.id.desc()).all()
    trexes = [trex.hostname for trex in get_trexes]
    list_trexes = [(trex, trex) for trex in trexes[1:]]
    list_trexes.insert(0, (trexes[0], '{} (Default)'.format(trexes[0])))
    # get devices list
    get_devices = models.Device.query.order_by(models.Device.id.desc()).all()
    devices = [device.name for device in get_devices]
    list_devices = [(device, device) for device in devices[1:]]
    list_devices.insert(0, (devices[0], '{} (Default)'.format(devices[0])))
    # get statuses list
    statuses = ['pending', 'hold']
    list_statuses = [(status, status) for status in statuses[1:]]
    list_statuses.insert(0, (statuses[0], '{} (Default)'.format(statuses[0])))

    class TaskForm(FlaskForm):
        # making form
        test = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(tests)],
            choices=list_tests,
            default=tests[0])
        trex = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(trexes)],
            choices=list_trexes,
            default=trexes[0])
        device = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(devices)],
            choices=list_devices,
            default=devices[0])
        description = TextAreaField(
            validators=[Required(), Length(min=1, max=1024)])
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        submit = SubmitField('Add new')

    # form
    form = TaskForm()
    # variables
    page_title = 'New Task'
    test = None
    trex = None
    device = None
    description = None
    status = None
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        test = form.test.data
        form.test.data = ''
        trex = form.trex.data
        form.trex.data = ''
        device = form.device.data
        form.device.data = ''
        description = form.description.data
        form.description.data = ''
        status = form.status.data
        form.status.data = ''
        # creates DB entry
        new_task = models.Task(test=test, trex=trex, device=device, description=description, status=status)
        # adding DB entry in DB
        db.session.add(new_task)
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> New task was added</div>'
        # showing form with success message
        return render_template('task_action.html', form=form, note='<p class="help-block">Note. All fields are required<p>', succ_msg=msg, page_title=page_title)

    return render_template('task_action.html', form=form, note='<p class="help-block">Note. All fields are required<p>', page_title=page_title)


@app.route('/task/<int:task_id>/delete/', methods=['GET', 'POST'])
def task_delete(task_id):
    task_entr = models.Task.query.get(task_id)
    # no task id return 404
    if not task_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting task ID {}'.format(task_id))
        submit = SubmitField('Delete task')

    form = DeleteForm()

    if form.checker.data:
        checker = form.checker.data
        print('checker', checker)
        form.checker.data = False
        db.session.delete(task_entr)
        db.session.commit()
        del_msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was deleted</div>'.format(task_id)
        return render_template('delete.html', del_msg=del_msg)

    return render_template('delete.html', form=form)


@app.route('/task/<int:task_id>/edit/', methods=['GET', 'POST'])
def task_edit(task_id):
    task_entr = models.Task.query.get(task_id)
    # no task id return 404
    if not task_entr:
        abort(404)

    # get tests list
    get_tests = models.Test.query.order_by(models.Test.id.desc()).all()
    tests = [test.name for test in get_tests]
    tests.remove(task_entr.test)
    tests.insert(0, task_entr.test)
    list_tests = ([(test, test) for test in tests])
    # get trexes list
    get_trexes = models.Trex.query.order_by(models.Trex.id.desc()).all()
    trexes = [trex.hostname for trex in get_trexes]
    trexes.remove(task_entr.trex)
    trexes.insert(0, task_entr.trex)
    list_trexes = [(trex, trex) for trex in trexes]
    # get devices list
    get_devices = models.Device.query.order_by(models.Device.id.desc()).all()
    devices = [device.name for device in get_devices]
    devices.remove(task_entr.device)
    devices.insert(0, task_entr.device)
    list_devices = [(device, device) for device in devices]
    # get statuses list
    statuses = ['pending', 'hold', 'canceled']
    statuses.remove(task_entr.status)
    statuses.insert(0, task_entr.status)
    list_statuses = [(status, status) for status in statuses]

    class TaskForm(FlaskForm):
        # making form
        test = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(tests)],
            choices=list_tests,
            default=tests[0])
        trex = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(trexes)],
            choices=list_trexes,
            default=trexes[0])
        device = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(devices)],
            choices=list_devices,
            default=devices[0])
        description = TextAreaField(
            validators=[Required(), Length(min=1, max=1024)],
            default=task_entr.description)
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        submit = SubmitField('Save task')

    # form
    form = TaskForm()
    # variables
    page_title = 'Edit Task'
    test = task_entr.test
    trex = task_entr.trex
    device = task_entr.device
    description = task_entr.description
    status = task_entr.status
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        test = form.test.data
        form.test.data = test
        trex = form.trex.data
        form.trex.data = trex
        device = form.device.data
        form.device.data = device
        description = form.description.data
        form.description.data = description
        status = form.status.data
        form.status.data = status
        # changing DB entry
        task_entr.test = test
        task_entr.trex = trex
        task_entr.device = device
        task_entr.description = description
        task_entr.status = status
        # save DB entry in DB
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was changed</div>'.format(task_entr.id)
        # showing form with success message
        return render_template('task_action.html', form=form, note='<p class="help-block">Note. All fields are required<p>', succ_msg=msg, page_title=page_title)

    return render_template('task_action.html', form=form, note='<p class="help-block">Note. All fields are required<p>', page_title=page_title)


@app.route('/task/<int:task_id>/hold/')
def task_hold(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'hold'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was holded</div>'.format(task_entr.id)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The task ID {} was not holded. No task ID</div>'.format(task_entr.id)
    return(msg)


@app.route('/task/<int:task_id>/queue/')
def task_queue(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'pending'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was queued</div>'.format(task_entr.id)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The task ID {} was not queued. No task ID</div>'.format(task_entr.id)
    return(msg)


@app.route('/task/<int:task_id>/cancel/')
def task_cancel(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'canceled'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was canceled</div>'.format(task_entr.id)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The task ID {} was not canceled. No task ID</div>'.format(task_entr.id)
    return(msg)


@app.route('/task/<int:task_id>/readd/')
def task_readd(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'pending'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The task ID {} was added again</div>'.format(task_entr.id)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The task ID {} was not added again. No task ID</div>'.format(task_entr.id)
    return(msg)


@app.route('/task/<int:task_id>/')
def task_show(task_id):
    task_entr = models.Task.query.get(task_id)
    # no task id return 404
    if not task_entr:
        abort(404)

    page_title = 'Task ID {} data'.format(task_id)
    if task_entr.result == 'error':
        content = '''<p class="lead">An error occured during test:</p>
        <blockquote>
            <p><em>"{}"</em></p>
        </blockquote>'''.format(loads(task_entr.data)['error'])
        return render_template(
            'task.html',
            content=content,
            page_title=page_title)
    elif task_entr.result == 'success':
        task_data = loads(task_entr.data)['trex']
        duration = loads(task_entr.tests.parameters)['trex']['duration']
        sampler = len(task_data['sampler'])
        graph_data = {}
        graph_data['intervals'] = [i * int(duration / sampler) for i in range(sampler + 1)]
        graph_data['tx_pps'] = [0] + [task_data['sampler'][i]['tx_pps'] for i in range(sampler)]
        graph_data['rx_pps'] = [0] + [task_data['sampler'][i]['rx_pps'] for i in range(sampler)]
        graph_data['expected_pps'] = [task_data['global']['expected_pps'] for i in range(sampler + 1)]
        graph_data['tx_bps'] = [0] + [task_data['sampler'][i]['tx_bps'] for i in range(sampler)]
        graph_data['rx_bps'] = [0] + [task_data['sampler'][i]['rx_bps'] for i in range(sampler)]
        graph_data['expected_bps'] = [task_data['global']['expected_bps'] for i in range(sampler + 1)]

        table_data_head = '''<div class="panel panel-default">
            <div class="panel-heading">{}</div>
        '''
        table_data_begin = '''<div class="table-responsive">
            <table class="table table-hover">'''
        table_data_global = '''
            <tr>
                <th>Expected pps rate</th>
                <th>Expected bps rate</th>
            </tr>
            <tr>
                <td>{expected_pps}</td>
                <td>{expected_bps}</td>
            </tr>
        '''.format(**task_data['global'])
        ports_data = {}
        for item in task_data['global']:
            if item in {'expected_pps', 'expected_bps'}:
                continue
            ports_data.update(task_data['global'][item])
        table_data_ports = '''
            <tr>
                <th>port num</th>
                <th>Packets TX</th>
                <th>Packets RX</th>
                <th>Bytes TX</th>
                <th>Bytes RX</th>
            </tr>
            <tr>
                <td>0</td>
                <td>{opackets-0}</td>
                <td>{ipackets-0}</td>
                <td>{obytes-0}</td>
                <td>{ibytes-0}</td>
            </tr>
            <tr>
                <td>1</td>
                <td>{opackets-1}</td>
                <td>{ipackets-1}</td>
                <td>{obytes-1}</td>
                <td>{ibytes-1}</td>
            </tr>
            '''.format(**ports_data)
        table_data_typical = '''
            <tr>
                <th>Packet rate pps TX</th>
                <th>Packet rate pps RX</th>
                <th>Bits rate bps TX</th>
                <th>Bits rate bps RX</th>
            </tr>
             <tr>
                <td>{tx_pps}</td>
                <td>{rx_pps}</td>
                <td>{tx_bps}</td>
                <td>{rx_bps}</td>
            </tr>
        '''.format(**task_data['typical'])
        table_end = '</table></div></div>'

        content = '''
            {0}
            {1}
            {2}'''.format(
                table_data_head.format('Global counters') + table_data_begin + table_data_global + table_end,
                table_data_head.format('Port counters') + table_data_begin + table_data_ports + table_end,
                table_data_head.format('Typical port counters') + table_data_begin + table_data_typical + table_end)

        return render_template(
            'task.html',
            graph=graph_data,
            content=content,
            page_title=page_title)
    else:
        content = '<p class="lead">Data for this task has not gathered yet.</p>'
        return render_template(
            'task.html',
            content=content,
            page_title=page_title)
