# task pages
# flask
from flask import render_template, abort
# DB
from app import app, db, models
# forms
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import Required, Length, AnyOf
# json for getting params
from json import loads
# helper for notes, buttons, etc
from app.helper import general_notes, humanize, tasks_statuses, messages, tasks_buttons
# test show func for task view
from app.tests import test_show
# killer for killing task
from task_scheduler import task_killer


@app.route('/tasks/')
def tasks_table(query=False, filtered_msg=False, filter_nav=True):
    '''shows table with tasks;
    query for performing especial queries for task condition like "hold, pending" or for showing task connected with test/trex/device;
    filtered message for showing "task was filtered by...";
    filter_nav for showing tasks nav bar'''

    # checking if any especial query for filtering task
    if not query:
        tasks_entr = models.Task.query.order_by(models.Task.id.desc()).all()
    # adding DB entries instead DB query
    elif isinstance(query, list):
        tasks_entr = query
    else:
        tasks_entr = models.Task.query.order_by(models.Task.id.desc()).all()
    # var for future filling
    table_data = ''
    # processing tasks
    for entr in tasks_entr:
        # checking status and sets html params for rows and buttons
        status_row = 'tr class="condition'
        if entr.result == 'success':
            status_row += ' success successful"'
        elif entr.result == 'error':
            status_row += ' danger error"'
        act_button = tasks_buttons['pending_hid'] + tasks_buttons['hold_hid'] + tasks_buttons['done_hid'] + tasks_buttons['canceled'] + tasks_buttons['testing_hid']
        if entr.status == 'pending':
            act_button = tasks_buttons['pending'] + tasks_buttons['hold_hid'] + tasks_buttons['done_hid'] + tasks_buttons['canceled_hid'] + tasks_buttons['testing_hid']
            status_row += ' pending"'
        elif entr.status == 'done':
            act_button = tasks_buttons['pending_hid'] + tasks_buttons['hold_hid'] + tasks_buttons['done'] + tasks_buttons['canceled_hid'] + tasks_buttons['testing_hid']
        elif entr.status == 'hold':
            act_button = tasks_buttons['pending_hid'] + tasks_buttons['hold'] + tasks_buttons['done_hid'] + tasks_buttons['canceled_hid'] + tasks_buttons['testing_hid']
            status_row += ' info hold"'
        elif entr.status == 'canceled':
            act_button = tasks_buttons['pending_hid'] + tasks_buttons['hold_hid'] + tasks_buttons['done_hid'] + tasks_buttons['canceled'] + tasks_buttons['testing_hid']
            status_row += ' active canceled"'
        elif entr.status == 'testing':
            act_button = tasks_buttons['pending_hid'] + tasks_buttons['hold_hid'] + tasks_buttons['done_hid'] + tasks_buttons['canceled_hid'] + tasks_buttons['testing']
            status_row += ' warning testing"'
        else:
            act_button = tasks_buttons['pending'] + tasks_buttons['hold_hid'] + tasks_buttons['done_hid'] + tasks_buttons['canceled_hid'] + tasks_buttons['testing_hid']
        # checing task result and sets html params for result labels
        if entr.result == 'success':
            res_label = 'success'
        elif entr.result == 'error':
            res_label = 'danger'
        elif entr.result == 'testing':
            res_label = 'warning'
        else:
            res_label = 'default'
        # cheking t-rex and device status and sets html params for statuses
        if entr.devices:
            if entr.devices.status == 'idle':
                dev_label = 'success'
            elif entr.devices.status == 'down':
                dev_label = 'muted'
            elif entr.devices.status == 'testing':
                dev_label = 'warning'
            else:
                dev_label = 'danger'
        if entr.trexes:
            if entr.trexes.status == 'idle':
                trex_label = 'success'
            elif entr.trexes.status == 'down':
                trex_label = 'muted'
            elif entr.trexes.status == 'testing':
                trex_label = 'warning'
            else:
                trex_label = 'danger'
        # cheking t-rex and device status and sets html params for mode labels
        if entr.tests:
            if entr.tests.mode == 'stateful':
                test_label = 'primary'
            elif entr.tests.mode == 'stateless':
                test_label = 'info'
        # gathering information for filling table
        table_items = {}
        # adding task db base info
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
            table_items['trex'] = '<a href="/trex/{1}">{0}</a><br /><small class="text-{2}">{3}</small>'.format(entr.trexes.hostname, entr.trexes.id, trex_label, entr.trexes.status)
        else:
            table_items['trex'] = '<em>TRex was deleted</em>'
        # device
        if entr.device:
            table_items['device'] = '<a href="/device/{1}">{0}</a><br /><small class="text-{2}">{3}</small>'.format(entr.devices.name, entr.devices.id, dev_label, entr.devices.status)
        else:
            table_items['device'] = '<em>Device was deleted</em>'
        # test
        table_items['test'] = '<a href="/test/{1}">{0}</a><br /><span class="label label-{3}">{2}</span>'.format(entr.tests.name, entr.tests.id, entr.tests.mode, test_label)
        # actions button
        table_items['act_button'] = act_button.format(entr.id)
        # result link
        if entr.status.lower() in {'done', 'error'} and str(entr.result).lower() in {'success', 'error'}:
            table_items['show'] = '<a href="/task/{0}">Show</a>'.format(entr.id)
        else:
            table_items['show'] = 'Is not collected yet'
        # making table row
        table_data += '''
            <{status_row}>
                <td>{id}</td>
                <td class="task_status">{status}<br /><span class="label label-{res_label}">{result}</span></td>
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
        # js script
        script_file = 'tasks.js'

    return render_template(
        'tasks.html',
        title='List of tasks',
        content=table_data,
        script_file=script_file,
        filtered_msg=filtered_msg,
        filter_nav=filter_nav)


@app.route('/task/new/', methods=['GET', 'POST'])
def task_create():
    # making new task
    # getting info for filling forms in especial order
    # geta tests list
    get_tests = models.Test.query.order_by(models.Test.id.desc()).all()
    tests = [test.name for test in get_tests]
    list_tests = ([(test, test) for test in tests[1:]])
    list_tests.insert(0, (tests[0], '{} (Default)'.format(tests[0])))
    # geta trexes list
    get_trexes = models.Trex.query.order_by(models.Trex.id.desc()).all()
    trexes = [trex.hostname for trex in get_trexes]
    list_trexes = [(trex, trex) for trex in trexes[1:]]
    list_trexes.insert(0, (trexes[0], '{} (Default)'.format(trexes[0])))
    # geta devices list
    get_devices = models.Device.query.order_by(models.Device.id.desc()).all()
    devices = [device.name for device in get_devices]
    list_devices = [(device, device) for device in devices[1:]]
    list_devices.insert(0, (devices[0], '{} (Default)'.format(devices[0])))
    # geta statuses list
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
            'TRex',
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
    # form obj
    form = TaskForm()
    # variables
    page_title = 'New Task'
    test = None
    trex = None
    device = None
    description = None
    status = None
    # require note
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        test = form.test.data
        trex = form.trex.data
        device = form.device.data
        description = form.description.data
        status = form.status.data
        # creates DB entry
        new_task = models.Task(
            test=test,
            trex=trex,
            device=device,
            description=description,
            status=status)
        # adding DB entry in DB
        db.session.add(new_task)
        db.session.commit()
        # success message
        msg = messages['success'].format('New task was added')
        # cleaning form fields
        form.test.data = None
        form.trex.data = None
        form.device.data = None
        form.description.data = None
        form.status.data = None
        # showing form with success message
        return render_template(
            'task_action.html',
            form=form,
            note=note,
            msg=msg,
            title=page_title)
    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'task_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)

    return render_template(
        'task_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/task/<int:task_id>/delete/', methods=['GET', 'POST'])
def task_delete(task_id):
    # deleting task from DB
    task_entr = models.Task.query.get(task_id)
    # no task id returns 404
    if not task_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting task ID {}'.format(task_id))
        submit = SubmitField('Delete task')
    # form obj
    form = DeleteForm()
    page_title = 'Task ID {} deleting confirmation'.format(task_id)
    # checking if checked
    if form.checker.data:
        db.session.delete(task_entr)
        # cleans form fields
        form.checker.data = False
        # if hidden test connected with current task exixts one needs to be deleted
        if task_entr.tests.hidden:
            db.session.delete(task_entr.tests)
        db.session.commit()
        del_msg = messages['succ_no_close'].format('The task ID {} was deleted'.format(task_id))
        return render_template(
            'delete.html',
            del_msg=del_msg,
            title=page_title)

    return render_template(
        'delete.html',
        form=form,
        title=page_title)


@app.route('/task/<int:task_id>/edit/', methods=['GET', 'POST'])
def task_edit(task_id):
    # edits existing task
    task_entr = models.Task.query.get(task_id)
    # no task id returns 404
    if not task_entr:
        abort(404)
    # getting info for filling forms in especial order, fields will equal current task values
    # geta tests list
    get_tests = models.Test.query.order_by(models.Test.id.desc()).all()
    tests = [test.name for test in get_tests]
    tests.remove(task_entr.test)
    tests.insert(0, task_entr.test)
    list_tests = ([(test, test) for test in tests])
    # geta trexes list
    get_trexes = models.Trex.query.order_by(models.Trex.id.desc()).all()
    trexes = [trex.hostname for trex in get_trexes]
    trexes.remove(task_entr.trex)
    trexes.insert(0, task_entr.trex)
    list_trexes = [(trex, trex) for trex in trexes]
    # geta devices list
    get_devices = models.Device.query.order_by(models.Device.id.desc()).all()
    devices = [device.name for device in get_devices]
    devices.remove(task_entr.device)
    devices.insert(0, task_entr.device)
    list_devices = [(device, device) for device in devices]
    # geta statuses list
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
    # require note
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
        # success message
        msg = messages['succ_no_close'].format('The task ID {} was changed</div>'.format(task_entr.id))
        # showing form with success message
        return render_template(
            'task_action.html',
            form=form,
            note=note,
            msg=msg,
            title=page_title)

    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'task_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)

    return render_template(
        'task_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/task/<int:task_id>/hold/')
def task_hold(task_id):
    # changing task status to hold
    task_entr = models.Task.query.get(task_id)
    # changing status
    if task_entr:
        task_entr.status = 'hold'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was holded'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not holded. No task ID {}'.format(task_entr.id))
    return msg


@app.route('/task/<int:task_id>/queue/')
def task_queue(task_id):
    # changing task status to pending
    task_entr = models.Task.query.get(task_id)
    # changing status
    if task_entr:
        task_entr.status = 'pending'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was queued'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not queued. No task ID {}'.format(task_entr.id))
    return msg


@app.route('/task/<int:task_id>/cancel/')
def task_cancel(task_id):
    # changing task status to canceled
    task_entr = models.Task.query.get(task_id)
    # changing status
    if task_entr:
        task_entr.status = 'canceled'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was canceled'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not canceled. No task ID {}'.format(task_entr.id))
    return msg


@app.route('/task/<int:task_id>/readd/')
def task_readd(task_id):
    # readding done task as new
    task_entr = models.Task.query.get(task_id)
    # changing task values
    if task_entr:
        # changing status
        task_entr.status = 'pending'
        # clean data
        task_entr.data = None
        task_entr.result = None
        task_entr.start_time = None
        task_entr.end_time = None
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The task ID {} was added again'.format(task_entr.id))
    else:
        msg = messages['no_succ'].format('The task ID {} was not added again. No task ID'.format(task_entr.id))
    return msg


@app.route('/task/<int:task_id>/')
def task_show(task_id):
    # showing task details
    task_entr = models.Task.query.get(task_id)
    # no task id returns 404
    if not task_entr:
        abort(404)
    page_title = 'Task ID {} data'.format(task_id)
    # cheking if task has error result and shows error info
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
    # if result is success gathering info for showing
    elif task_entr.result == 'success':
        # gets task data
        task_data = loads(task_entr.data)['trex']
        duration = loads(task_entr.tests.parameters)['trex']['duration']
        sampler = len(task_data['sampler'])
        # gathering chart info
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
        # table head and bgin
        table_data_head = '''<div class="panel panel-default">
            <div class="panel-heading">{}</div>'''
        table_data_begin = '''<div class="table-responsive">
            <table class="table table-hover">'''
        # table with global data
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
        # calculating percents losses from flow
        if ports_data['opackets-0'] != 0:
            ports_data['perc-0'] = '{:.4f}'.format((abs(ports_data['losses-0']) * 100) / ports_data['opackets-0'])
        else:
            ports_data['perc-0'] = ''
        if ports_data['opackets-1'] != 0:
            ports_data['perc-1'] = '{:.4f}'.format((abs(ports_data['losses-1']) * 100) / ports_data['opackets-1'])
        else:
            ports_data['perc-1'] = ''
        # humanize counters output
        for item in ports_data:
            if 'byte' in item:
                ports_data[item] = humanize(ports_data[item], units='nist')
            elif 'packet' in item or 'loss' in item:
                ports_data[item] = humanize(ports_data[item])
        # table with port counters
        table_data_ports = '''
            <tr>
                <th>Port #</th>
                <th>Packets TX</th>
                <th>Packets RX</th>
                <th>Bytes TX</th>
                <th>Bytes RX</th>
                <th>Computed losses</th>
                <th>% from flow</th>
                <th>TRex drops</th>
            </tr>
            <tr>
                <td>0</td>
                <td>{opackets-0}</td>
                <td>{ipackets-0}</td>
                <td>{obytes-0}</td>
                <td>{ibytes-0}</td>
                <td>{losses-0}</td>
                <td>{perc-0}</td>
                <td>{0}</td>
            </tr>
            <tr>
                <td>1</td>
                <td>{opackets-1}</td>
                <td>{ipackets-1}</td>
                <td>{ibytes-1}</td>
                <td>{obytes-1}</td>
                <td>{losses-1}</td>
                <td>{perc-1}</td>
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
        # table with typical data
        table_data_typical = '''
            <tr>
                <th>Packet rate pps TX</th>
                <th>Packet rate pps RX</th>
                <th>Bits rate bps TX</th>
                <th>Bits rate bps RX</th>
                <th>TRex RX Drops bps</th>
                <th>TRex queue drops</th>
                <th>TRex queue full</th>
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
        # collecting all data together
        content = '''
            {0}
            {1}
            {2}
        '''.format(
            table_data_head.format('Global counters') + table_data_begin + table_data_global + table_end,
            table_data_head.format('Port counters') + table_data_begin + table_data_ports + table_end,
            table_data_head.format('Typical port counters') + table_data_begin + table_data_typical + table_end)
        # test data table
        test_data = test_show(task_entr.tests.id, page=False)
        # if test is deleted show message
        test_hidden_msg = False
        if task_entr.tests.hidden:
            test_hidden_msg = 'This test was deleted and is not availaible'
        # trex data table
        trex_data = '''
        <tr>
            <td>{0}</td>
            <td>{1}</td>
        </tr>'''.format(*(task_entr.trex, task_entr.trexes.description) if task_entr.trex else ('TRex was deleted', ''))
        # device data table
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
        # shows no data if no data for this task
        content = '<p class="lead">Data for this task has not gathered yet.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)


@app.route('/tasks/<query_item>/<int:item_id>/')
def task_items(query_item, item_id):
    # returns task table filtered by test/trex/device
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
    # if not entr id returns 404
    if not item:
        abort(404)
    # checking DB entr name hostname for trex and name for device
    item_name = item.hostname if item_name == 'hostname' else item.name
    # getting task list for entr
    tasks = item.tasks
    # if not any tasks shows no task
    if len(tasks) == 0:
        page_title = 'List of tasks'
        content = '<p class="lead">There are not approptiate tasks.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)
    # resort task lower id is located lower
    tasks.reverse()
    # message task filtered by...
    filtered_msg = '{} <em>{}</em>'.format(query_item, item_name)

    return tasks_table(query=tasks, filtered_msg=filtered_msg)


@app.route('/tasks/<condition>/')
def task_condition(condition):
    # returns task table filtered by task condition like "hold, testing"
    # checking if rigth condition
    if condition in tasks_statuses['all']:
        # getting tasks with condition
        tasks = models.Task.query.filter(models.Task.status == condition).order_by(models.Task.id.desc()).all()
    else:
        # no condition returns 404
        abort(404)
    # message task filtered by...
    filtered_msg = '<em>{}</em> status'.format(condition)
    # if not any tasks shows no task
    if not tasks:
        page_title = 'List of tasks'
        content = '<p class="lead">There are not approptiate tasks.</p>'
        return render_template(
            'task.html',
            content=content,
            title=page_title,
            no_data=True)

    return tasks_table(query=tasks, filtered_msg=filtered_msg, filter_nav=False)


@app.route('/task/<int:task_id>/clone/')
def clone_task(task_id):
    # clones task and adds one as new with hold status
    task_entr = models.Task.query.get(task_id)
    if task_entr:
        # creates new DB entry
        new_task = models.Task(
            test=task_entr.test,
            trex=task_entr.trex,
            device=task_entr.device,
            # gets description from origin task
            description='Cloned task ID {}: "{}"'.format(task_entr.id, task_entr.description[:987]),
            status='hold')
        # adding DB entry in DB
        db.session.add(new_task)
        db.session.commit()
        msg = messages['succ_no_close_time'].format('The task ID {} was cloned.'.format(task_entr.id), seconds='5')
    else:
        msg = messages['no_succ'].format('The task ID {} was not cloned. No task ID {}'.format(task_entr.id))

    return msg


@app.route('/task/<int:task_id>/kill/')
def kill_trex_tasks(task_id):
    # kills task from trex execution with "canceled" status
    task_entr = models.Task.query.get(task_id)
    # checking task and status
    if task_entr:
        if task_entr.status == 'testing':
            # trying to kill status as queue in redis and active trex task
            result = task_killer(task_entr)
            if result['status']:
                msg = messages['success'].format('Task ID {} was killed.'.format(task_id))
            # shows error info if task was not deleted
            else:
                msg = messages['danger'].format('''<p>Tasks ID {0} was not killed due TRex error:</p>
                    <blockquote>
                        <p>{1}</p>
                    </blockquote>'''.format(task_id, result['state']))
        # if task has not got "testing" status returns message

        else:
            msg = messages['warning'].format('Tasks ID {} was not killed. The task is not in testing state now'.format(task_id))
    else:
        # if not task id returns 404
        abort(404)
    return msg
