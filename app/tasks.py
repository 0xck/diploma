from flask import render_template, abort
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import Required, Length, AnyOf
from json import loads
from app.helper import general_notes, humanize, tasks_statuses, messages
from app.tests import test_show


@app.route('/tasks/')
def tasks_table(query=False, filtered_msg=False, filter_nav=True):
    # checking if any especial query for filtering task
    if not query:
        tasks_entr = models.Task.query.order_by(models.Task.id.desc()).all()
    elif isinstance(query, list):
        tasks_entr = query
    else:
        tasks_entr = models.Task.query.order_by(models.Task.id.desc()).all()
    table_data = ''
    act_button_template = {
        'begin': '''<div class="btn-group">
                        <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
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
        status_row = 'tr class="condition'
        if entr.result == 'success':
            status_row += ' success successful"'
        elif entr.result == 'error':
            status_row += ' danger error"'
        act_button = act_button_template['begin']
        if entr.status == 'pending':
            act_button += act_button_template['hold'] + act_button_template['separator'] + act_button_template['cancel'] + act_button_template['end']
            status_row += ' pending"'
        elif entr.status == 'done':
            act_button += act_button_template['readd'] + act_button_template['end']
        elif entr.status == 'hold':
            act_button += act_button_template['queue'] + act_button_template['separator'] + act_button_template['cancel'] + act_button_template['end']
            status_row += ' info hold"'
        elif entr.status == 'canceled':
            act_button += act_button_template['readd'] + act_button_template['end']
            status_row += ' active canceled"'
        elif entr.status == 'testing':
            # unactive button
            act_button = '''<div class="btn-group">
                        <button type="button" class="btn btn-default dropdown-toggle " data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>'''
            status_row += ' warning testing"'
        else:
            act_button += act_button_template['hold'] + act_button_template['queue'] + act_button_template['separator'] + act_button_template['readd'] + act_button_template['cancel'] + act_button_template['end']

        if entr.result == 'success':
            res_label = 'success'
        elif entr.result == 'error':
            res_label = 'danger'
        elif entr.result == 'testing':
            res_label = 'warning'
        else:
            res_label = 'default'
        if entr.devices:
            if entr.devices.status == 'idle':
                dev_label = '#008000'
            elif entr.devices.status == 'down':
                dev_label = '#7F7F7F'
            elif entr.devices.status == 'testing':
                dev_label = '#FF8000'
            else:
                dev_label = '#800000'
        if entr.trexes:
            if entr.trexes.status == 'idle':
                trex_label = '#008000'
            elif entr.trexes.status == 'down':
                trex_label = '#7F7F7F'
            elif entr.trexes.status == 'testing':
                trex_label = '#FF8000'
            else:
                trex_label = '#800000'

        table_items = {}
        # adding task db info
        table_items.update(entr['ALL_DICT'])
        table_items['status_row'] = status_row
        table_items['res_label'] = res_label
        # task duration
        if entr.end_time is None or entr.start_time is None:
            table_items['duration'] = None
        else:
            table_items['duration'] = (entr.end_time - entr.start_time)
        # trex
        if entr.trexes:
            table_items['trex'] = '<a href="/trex/{1}">{0}</a><br /><small style="color:{2}";>{3}</small>'.format(entr.trexes.hostname, entr.trexes.id, trex_label, entr.trexes.status)
        else:
            table_items['trex'] = '<em>T-rex was deleted</em>'
        # device
        if entr.device:
            table_items['device'] = '<a href="/device/{1}">{0}</a><br /><small style="color:{2}";>{3}</small>'.format(entr.devices.name, entr.devices.id, dev_label, entr.devices.status)
        else:
            table_items['device'] = '<em>Device was deleted</em>'
        # test
        table_items['test'] = '<a href="/test/{1}">{0}</a><br /><small>{2}</small>'.format(entr.tests.name, entr.tests.id, entr.tests.mode)
        # actions button
        table_items['act_button'] = act_button.format(entr.id)
        # result link
        if entr.status.lower() in {'done', 'error'} and str(entr.result).lower() in {'success', 'error'}:
            table_items['show'] = '<a href="/task/{0}">Show</a>'.format(entr.id)
        else:
            table_items['show'] = 'Is not collected yet'

        table_data += '''
            <{status_row}>
                <td>{id}</td>
                <td class="task_status">{status}<br /><span class="label label-{res_label}">{result}</span></span></td>
                <td><small>{description}</small></td>
                <td><small>{start_time}<br />{end_time}</small></td>
                <td>{duration}</td>
                <td>{test}</td>
                <td>{trex}</td>
                <td>{device}</td>
                <td>{act_button}</td>
                <td>{show}</td>
            </tr>
        '''.format(**table_items)

    return render_template(
        'tasks.html',
        title='List of tasks',
        content=table_data,
        script_file='tasks.js',
        filtered_msg=filtered_msg,
        filter_nav=filter_nav)


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
    statuses = tasks_statuses['gui_new']
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
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
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
        msg = messages['success'].format('New task was added')
        # showing form with success message
        return render_template('task_action.html', form=form, note=note, msg=msg, title=page_title)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0]))
        return render_template('task_action.html', form=form, note=note, title=page_title, msg=msg)
    return render_template('task_action.html', form=form, note=note, title=page_title)


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
    page_title = 'Task ID {} deleting confirmation'.format(task_id)

    if form.checker.data:
        form.checker.data = False
        db.session.delete(task_entr)
        # hidden test connected with current task exixts one needs to be deleted
        if task_entr.tests.hidden:
            db.session.delete(task_entr.tests)
        db.session.commit()
        del_msg = messages['succ_no_close'].format('The task ID {} was deleted'.format(task_id))
        return render_template('delete.html', del_msg=del_msg, title=page_title)

    return render_template('delete.html', form=form, title=page_title)


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
    statuses = tasks_statuses['all']
    statuses.remove(task_entr.status)
    statuses.insert(0, task_entr.status)
    list_statuses = [(status, status) for status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('done', 'done'))

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
    page_title = 'Edit Task ID {}'.format(task_id)
    test = task_entr.test
    trex = task_entr.trex
    device = task_entr.device
    description = task_entr.description
    status = task_entr.status
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
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
        msg = messages['succ_no_close'].format('The task ID {} was changed</div>'.format(task_entr.id))
        # showing form with success message
        return render_template('task_action.html', form=form, note=note, msg=msg, title=page_title)

    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0]))
        return render_template('task_action.html', form=form, note=note, title=page_title, msg=msg)
    return render_template('task_action.html', form=form, note=note, title=page_title)


@app.route('/task/<int:task_id>/hold/')
def task_hold(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'hold'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was holded'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not holded. No task ID {}'.format(task_entr.id))
    return(msg)


@app.route('/task/<int:task_id>/queue/')
def task_queue(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'pending'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was queued'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not queued. No task ID {}'.format(task_entr.id))
    return(msg)


@app.route('/task/<int:task_id>/cancel/')
def task_cancel(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'canceled'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was canceled'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not canceled. No task ID {}'.format(task_entr.id))
    return(msg)


@app.route('/task/<int:task_id>/readd/')
def task_readd(task_id):
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        task_entr.status = 'pending'
        task_entr.data = None
        task_entr.result = None
        task_entr.start_time = None
        task_entr.end_time = None
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was added again'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not added again. No task ID'.format(task_entr.id))
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
            title=page_title,
            no_data=True)
    elif task_entr.result == 'success':
        task_data = loads(task_entr.data)['trex']
        duration = loads(task_entr.tests.parameters)['trex']['duration']
        sampler = len(task_data['sampler'])
        graph_data = {}
        graph_data['intervals'] = [i * int(duration / sampler) for i in range(sampler + 1)]
        graph_data['tx_pps'] = [0] + [task_data['sampler'][i]['tx_pps'] for i in range(sampler)]
        graph_data['rx_pps'] = [0] + [task_data['sampler'][i]['rx_pps'] for i in range(sampler)]
        graph_data['expected_pps'] = [task_data['global']['expected_pps'] for i in range(sampler + 1)]
        graph_data['queue_drop'] = [0] + [task_data['sampler'][i]['queue_drop'] for i in range(sampler)]
        graph_data['queue_full'] = [0] + [task_data['sampler'][i]['queue_full'] for i in range(sampler)]
        graph_data['tx_bps'] = [0] + [task_data['sampler'][i]['tx_bps'] for i in range(sampler)]
        graph_data['rx_bps'] = [0] + [task_data['sampler'][i]['rx_bps'] for i in range(sampler)]
        graph_data['expected_bps'] = [task_data['global']['expected_bps'] for i in range(sampler + 1)]
        graph_data['rx_drop_bps'] = [0] + [task_data['sampler'][i]['rx_drop_bps'] for i in range(sampler)]
        table_data_head = '''<div class="panel panel-default">
            <div class="panel-heading">{}</div>'''
        table_data_begin = '''<div class="table-responsive">
            <table class="table table-hover">'''
        table_data_global = '''
            <tr>
                <th>Expected pps rate</th>
                <th>Expected bps rate</th>
            </tr>
            <tr>
                <td>{0}</td>
                <td>{1}</td>
            </tr>
        '''.format(
            humanize(task_data['global']['expected_pps']),
            humanize(task_data['global']['expected_bps'], units='nist'))
        # cheking for drops
        drop = False
        for drop_count in task_data['sampler']:
            if int(drop_count['rx_drop_bps']) or int(drop_count['queue_full']) > 0:
                drop = True
                break
        # getting port counters
        ports_data = {}
        for item in task_data['global']:
            if item in {'expected_pps', 'expected_bps'}:
                continue
            ports_data.update(task_data['global'][item])
        # calculating losses
        ports_data['losses-0'] = ports_data['ipackets-1'] - ports_data['opackets-0']
        ports_data['losses-1'] = ports_data['ipackets-0'] - ports_data['opackets-1']
        # humanize counters output
        for item in ports_data:
            if 'byte' in item:
                ports_data[item] = humanize(ports_data[item], units='nist')
            elif 'packet' in item or 'loss' in item:
                ports_data[item] = humanize(ports_data[item])
        table_data_ports = '''
            <tr>
                <th>Port #</th>
                <th>Packets TX</th>
                <th>Packets RX</th>
                <th>Bytes TX</th>
                <th>Bytes RX</th>
                <th>Computed losses</th>
                <th>T-rex drops</th>
            </tr>
            <tr>
                <td>0</td>
                <td>{opackets-0}</td>
                <td>{ipackets-0}</td>
                <td>{obytes-0}</td>
                <td>{ibytes-0}</td>
                <td>{losses-0}</td>
                <td>{0}</td>
            </tr>
            <tr>
                <td>1</td>
                <td>{opackets-1}</td>
                <td>{ipackets-1}</td>
                <td>{ibytes-1}</td>
                <td>{obytes-1}</td>
                <td>{losses-1}</td>
                <td>{0}</td>
            </tr>
        '''.format(
            True if drop else None,
            **ports_data)
        # humanize typical output
        for item in task_data['typical']:
            if 'bps' in item:
                task_data['typical'][item] = humanize(task_data['typical'][item], units='nist')
            elif 'pps' in item:
                task_data['typical'][item] = humanize(task_data['typical'][item])
        table_data_typical = '''
            <tr>
                <th>Packet rate pps TX</th>
                <th>Packet rate pps RX</th>
                <th>Bits rate bps TX</th>
                <th>Bits rate bps RX</th>
                <th>T-rex RX Drops bps</th>
                <th>T-rex queue drops</th>
                <th>T-rex queue full</th>
            </tr>
             <tr>
                <td>{tx_pps}</td>
                <td>{rx_pps}</td>
                <td>{tx_bps}</td>
                <td>{rx_bps}</td>
                <td>{rx_drop_bps}</td>
                <td>{queue_drop}</td>
                <td>{queue_full}</td>
            </tr>
        '''.format(**task_data['typical'])
        table_end = '</table></div></div>'

        content = '''
            {0}
            {1}
            {2}
        '''.format(
            table_data_head.format('Global counters') + table_data_begin + table_data_global + table_end,
            table_data_head.format('Port counters') + table_data_begin + table_data_ports + table_end,
            table_data_head.format('Typical port counters') + table_data_begin + table_data_typical + table_end)
        test_data = test_show(task_entr.tests.id, page=False)
        test_hidden_msg = False
        if task_entr.tests.hidden:
            test_hidden_msg = 'This test was deleted and is not availaible'

        trex_data = '''
        <tr>
            <td>{0}</td>
            <td>{1}</td>
        </tr>'''.format(*(task_entr.trex, task_entr.trexes.description) if task_entr.trex else ('T-rex was deleted', ''))
        device_data = '''
        <tr>
            <td>{0}</td>
            <td>{1}</td>
        </tr>'''.format(*(task_entr.device, task_entr.devices.description) if task_entr.device else ('Device was deleted', ''))

        return render_template(
            'task.html',
            graph=graph_data,
            content=content,
            title=page_title,
            test_data=test_data,
            test_hidden=test_hidden_msg,
            trex_data=trex_data,
            device_data=device_data)
    else:
        content = '<p class="lead">Data for this task has not gathered yet.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)


@app.route('/tasks/<query_item>/<int:item_id>/')
def task_items(query_item, item_id):
    item_name = 'name'
    if query_item == 'trex':
        item = models.Trex.query.get(item_id)
        item_name = 'hostname'
    elif query_item == 'device':
        item = models.Device.query.get(item_id)
    elif query_item == 'test':
        item = models.Test.query.get(item_id)
    else:
        abort(404)
    if not item:
        abort(404)
    item_name = item.hostname if item_name == 'hostname' else item.name
    tasks = item.tasks
    if len(tasks) == 0:
        page_title = 'List of tasks'
        content = '<p class="lead">There are not approptiate tasks.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)
    tasks.reverse()
    filtered_msg = '{} <em>{}</em>'.format(query_item, item_name)

    return tasks_table(query=tasks, filtered_msg=filtered_msg)


@app.route('/tasks/<condition>/')
def task_condition(condition):
    if condition in tasks_statuses['all']:
        tasks = models.Task.query.filter(models.Task.status == condition).order_by(models.Task.id.desc()).all()
    else:
        abort(404)
    filtered_msg = '<em>{}</em> status'.format(condition)
    if not tasks:
        page_title = 'List of tasks'
        content = '<p class="lead">There are not approptiate tasks.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)

    return tasks_table(query=tasks, filtered_msg=filtered_msg, filter_nav=False)
