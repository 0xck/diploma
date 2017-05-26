from flask import render_template, abort, redirect
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, BooleanField, StringField, IntegerField, FloatField
from wtforms.validators import Required, Length, AnyOf, NumberRange, Regexp, NoneOf
from app.helper import stf_traffic_patterns, stf_notes, stl_notes, general_notes, validator_err, messages, test_types, stl_test_val, sel_test_types
from json import loads, dumps
from os import listdir, getcwd, path


@app.route('/tests/')
def tests_table():
    tests_entr = models.Test.query.filter(models.Test.hidden == False).order_by(models.Test.id.desc()).all()
    table_data = ''
    act_button_template = {
        'begin': '''<div class="btn-group">
                        <button type="button" class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">''',
        'end': '''<li><a href="/test/{0}/edit/{1}" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/test/{0}/delete" class="delete" id="{0}">Delete</a></li>
                </ul>
            </div>'''
    }

    for entr in tests_entr:
        act_button = act_button_template['begin'] + act_button_template['end']
        table_items = {}
        # getting test db info
        table_items.update(entr['ALL_DICT'])
        # action button
        if entr.mode == 'stateful':
            table_items['act_button'] = act_button.format(entr.id, 'stf')
        else:
            table_items['act_button'] = act_button.format(entr.id, 'stl')
        # details
        table_items['show'] = '<a href="/test/{0}">Show</a>'.format(entr.id)
        # associated tasks
        table_items['tasks'] = '<a href="/tasks/test/{0}">Show tasks</a>'.format(entr.id)

        table_data += '''
            <tr>
                <td>{id}</td>
                <td>{name}</td>
                <td>{mode}</td>
                <td>{test_type}</td>
                <td><small>{description}</small></td>
                <td>{act_button}</td>
                <td>{show}</td>
                <td>{tasks}</td>
            </tr>
        '''.format(**table_items)

    return render_template(
        'tests.html',
        title='List of tests',
        content=table_data,
        script_file='tests.js')


@app.route('/test/new/stf/', methods=['GET', 'POST'])
def test_create_stf():
    mode = 'stateful'
    # getting test type list
    types = test_types
    list_types = [(test_type, test_type) for test_type in types[1:]]
    list_types.insert(0, (types[0], '{} (Default)'.format(types[0])))
    # getting patterns list
    patterns = stf_traffic_patterns
    list_patterns = [(test_pattern, test_pattern) for test_pattern in patterns[1:]]
    list_patterns.insert(0, (patterns[0], '{} (Default)'.format(patterns[0])))
    # getting types of selection test
    selection_types = sel_test_types['all']
    list_selection_types = [(sel_type, sel_type) for sel_type in selection_types[1:]]
    list_selection_types.insert(0, (selection_types[0], '{} (Default)'.format(selection_types[0])))
    # getting lists of current tests values for checking
    curr_tests = models.Test.query.all()
    curr_name = []
    if len(curr_tests) > 0:
        for curr_test in curr_tests:
            curr_name.append(curr_test.name)

    class TestForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])])
        # general test params
        test_type = SelectField(
            label='Test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(types)],
            choices=list_types,
            default=types[0])
        duration = IntegerField(
            label='Duration time in seconds',
            validators=[Required(), NumberRange(min=30, max=86400)],
            default=60)
        traffic_pattern = SelectField(
            label='Traffic pattern',
            validators=[Required(), Length(min=1, max=1024), AnyOf(patterns)],
            choices=list_patterns,
            default=patterns[0])
        multiplier = FloatField(
            validators=[Required(), NumberRange(min=0.0001, max=100000)],
            default=1)
        sampler = IntegerField(
            label='Sampler time in seconds',
            validators=[Required(), NumberRange(min=1, max=600)],
            default=1)
        # selection test params
        accuracy = FloatField(
            label='Accuracy of test result in percents',
            validators=[Required(), NumberRange(min=0.0000000001, max=100)],
            default=0.1)
        rate_incr_step = FloatField(
            label='Rate step',
            validators=[Required(), NumberRange(min=0.0001, max=100000)],
            default=1)
        max_succ_attempt = IntegerField(
            label='Maximum successful attemps for accepting result',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=3)
        max_test_count = IntegerField(
            label='Maximum number of test iterations',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=30)
        selection_test_type = SelectField(
            label='Selection test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(selection_types)],
            choices=list_selection_types,
            default=selection_types[0])
        # other parameters
        warm = IntegerField(
            label='Warm time in seconds',
            validators=[Required(), NumberRange(min=1, max=900)],
            default=10)
        wait = IntegerField(
            label='NIC initial delay in seconds',
            validators=[Required(), NumberRange(min=1, max=10)],
            default=1)
        soft_test = BooleanField(label='Check if T-rex is software appliance', default=True)
        hw_chsum = BooleanField(label="Check if T-rex's NICs support HW offloading", default=False)
        description = TextAreaField(
            validators=[Length(max=1024)])
        # submit
        submit = SubmitField('Add new')
    # form
    form = TestForm()
    # variables
    page_title = 'New stateful test'
    script_file = 'tests.js'
    name = None
    test_type = types[0]
    duration = None
    traffic_pattern = None
    multiplier = None
    accuracy = None
    rate_incr_step = None
    max_succ_attempt = None
    max_test_count = None
    selection_test_type = None
    sampler = None
    warm = None
    wait = None
    soft_test = True
    hw_chsum = False
    description = ''
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    notes = stf_notes

    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        form.name.data = None
        test_type = form.test_type.data
        form.test_type.data = None
        duration = int(form.duration.data)
        form.duration.data = 60
        traffic_pattern = form.traffic_pattern.data
        form.traffic_pattern.data = ''
        multiplier = float(form.multiplier.data)
        form.multiplier.data = 1
        # selection
        accuracy = (float(form.accuracy.data) / 100)
        form.accuracy.data = 0.1
        rate_incr_step = float(form.rate_incr_step.data)
        form.rate_incr_step.data = 1
        max_succ_attempt = int(form.max_succ_attempt.data)
        form.max_succ_attempt.data = 3
        max_test_count = int(form.max_test_count.data)
        form.max_test_count.data = 30
        selection_test_type = form.selection_test_type.data
        form.selection_test_type.data = ''
        # other
        sampler = int(form.sampler.data)
        form.sampler.data = 1
        warm = int(form.warm.data)
        form.warm.data = 10
        wait = int(form.wait.data)
        form.wait.data = 1
        soft_test = form.soft_test.data
        form.soft_test.data = True
        hw_chsum = form.hw_chsum.data
        form.hw_chsum.data = False
        description = form.description.data
        form.description.data = ''

        # creates DB entry
        trex_params = dict(
            duration=duration,
            traffic_pattern=traffic_pattern,
            multiplier=multiplier,
            sampler=sampler,
            warm=warm,
            wait=wait,
            soft_test=soft_test,
            hw_chsum=hw_chsum)
        rate_params = dict(
            accuracy=accuracy,
            rate=multiplier,
            rate_incr_step=rate_incr_step,
            max_succ_attempt=max_succ_attempt,
            max_test_count=max_test_count,
            test_type=selection_test_type)

        new_test = models.Test(
            name=name,
            mode=mode,
            test_type=test_type,
            description=description,
            hidden=False,
            parameters=dumps(dict(trex=trex_params) if test_type == 'common' else dict(trex=trex_params, rate=rate_params)))
        # adding DB entry in DB
        db.session.add(new_test)
        db.session.commit()
        # Success message
        msg = messages['success'].format('New test was added')
        # showing form with success message
        return render_template('test_action.html', form=form, notes=notes, note=note, title=page_title, script_file=script_file, msg=msg, test_type=test_type, mode=mode)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template('test_action.html', form=form, notes=notes, note=note, title=page_title, script_file=script_file, msg=msg, test_type=test_type, mode=mode)
    # return clean form
    return render_template('test_action.html', form=form, notes=notes, note=note, title=page_title, script_file=script_file, test_type=test_type, mode=mode)


@app.route('/test/<int:test_id>/delete/', methods=['GET', 'POST'])
def test_delete(test_id):
    test_entr = models.Test.query.get(test_id)
    # no task id return 404
    if not test_entr or test_entr.hidden:
        abort(404)

    if test_entr.tasks:
        print('ok', test_entr.tasks)
    else:
        print('not ok', test_entr.tasks)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting test {}'.format(test_entr.name))
        submit = SubmitField('Delete test')

    form = DeleteForm()
    page_title = 'Test {} deleting confirmation'.format(test_entr.name)

    if form.checker.data:
        form.checker.data = False
        # even one task exists need to hide test
        if test_entr.tasks:
            test_entr.hidden = True
        # in case no tasks for test deletes test
        else:
            db.session.delete(test_entr)
        db.session.commit()
        del_msg = messages['succ_no_close'].format('The test {} was deleted'.format(test_entr.name))
        return render_template('delete.html', del_msg=del_msg, title=page_title)

    return render_template('delete.html', form=form, title=page_title)


@app.route('/test/<int:test_id>/edit/stf/', methods=['GET', 'POST'])
def test_edit_stf(test_id):
    mode = 'stateful'
    test_entr = models.Test.query.get(test_id)
    # no task id return 404
    if not test_entr or test_entr.hidden:
        abort(404)
    elif test_entr.mode != mode:
        return redirect('/test/{}/edit/stl/'.format(test_id))
    # getting test type list
    types = test_types
    list_types = [(test_type, test_type) for test_type in types]
    types.remove(test_entr.test_type)
    types.insert(0, test_entr.test_type)

    test_papams_trex = loads(test_entr.parameters)['trex']
    # getting patterns list
    patterns = stf_traffic_patterns
    list_patterns = [(test_pattern, test_pattern) for test_pattern in patterns]
    patterns.remove(test_papams_trex['traffic_pattern'])
    patterns.insert(0, test_papams_trex['traffic_pattern'])
    # getting rate params
    try:
        test_papams_rate = loads(test_entr.parameters)['rate']
    except KeyError:
        test_papams_rate = dict(
            accuracy=0.1,
            rate_incr_step=1,
            max_succ_attempt=3,
            max_test_count=30,
            test_type='safe')
    # getting types of selection test
    selection_types = sel_test_types['all']
    list_selection_types = [(sel_type, sel_type) for sel_type in selection_types]
    selection_types.remove(test_papams_rate['test_type'])
    selection_types.insert(0, test_papams_rate['test_type'])
    # getting lists of current tests values for checking
    curr_tests = models.Test.query.filter(models.Test.id != test_id).all()
    curr_name = []
    if len(curr_tests) > 0:
        for curr_test in curr_tests:
            curr_name.append(curr_test.name)

    class TestForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])],
            default=test_entr.name)
        # general test params
        test_type = SelectField(
            label='Test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(types)],
            choices=list_types,
            default=types[0])
        duration = IntegerField(
            label='Duration time in seconds',
            validators=[Required(), NumberRange(min=30, max=86400)],
            default=test_papams_trex['duration'])
        traffic_pattern = SelectField(
            label='Traffic pattern',
            validators=[Required(), Length(min=1, max=1024), AnyOf(patterns)],
            choices=list_patterns,
            default=patterns[0])
        multiplier = FloatField(
            validators=[Required(), NumberRange(min=0.0001, max=100000)],
            default=test_papams_trex['multiplier'])
        sampler = IntegerField(
            label='Sampler time in seconds',
            validators=[Required(), NumberRange(min=1, max=600)],
            default=test_papams_trex['sampler'])
        # selection test params
        accuracy = FloatField(
            label='Accuracy of test result in percents',
            validators=[Required(), NumberRange(min=0.0000000001, max=100)],
            default=test_papams_rate['accuracy'])
        rate_incr_step = FloatField(
            label='Rate step',
            validators=[Required(), NumberRange(min=0.0001, max=100000)],
            default=test_papams_rate['rate_incr_step'])
        max_succ_attempt = IntegerField(
            label='Maximum successful attemps for accepting result',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=test_papams_rate['max_succ_attempt'])
        max_test_count = IntegerField(
            label='Maximum number of test iterations',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=test_papams_rate['max_test_count'])
        selection_test_type = SelectField(
            label='Selection test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(selection_types)],
            choices=list_selection_types,
            default=selection_types[0])
        # other parameters
        warm = IntegerField(
            label='Warm time in seconds',
            validators=[Required(), NumberRange(min=1, max=900)],
            default=test_papams_trex['warm'])
        wait = IntegerField(
            label='NIC initial delay in seconds',
            validators=[Required(), NumberRange(min=1, max=10)],
            default=test_papams_trex['wait'])
        soft_test = BooleanField(label='Check if T-rex is software appliance', default=test_papams_trex['soft_test'])
        hw_chsum = BooleanField(label="Check if T-rex's NICs support HW offloading", default=test_papams_trex['hw_chsum'])
        description = TextAreaField(
            validators=[Length(max=1024)], default=test_entr.description)
        # submit
        submit = SubmitField('Save test')
    # form
    form = TestForm()
    # variables
    page_title = 'Edit stateful test {}'.format(test_entr.name)
    script_file = 'tests.js'
    name = None
    test_type = types[0]
    duration = None
    traffic_pattern = None
    multiplier = None
    accuracy = None
    rate_incr_step = None
    max_succ_attempt = None
    max_test_count = None
    selection_test_type = None
    sampler = None
    warm = None
    wait = None
    soft_test = True
    hw_chsum = False
    description = ''
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    notes = stf_notes

    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        test_type = form.test_type.data
        duration = int(form.duration.data)
        traffic_pattern = form.traffic_pattern.data
        multiplier = float(form.multiplier.data)
        # selection
        accuracy = (float(form.accuracy.data) / 100)
        rate_incr_step = float(form.rate_incr_step.data)
        max_succ_attempt = int(form.max_succ_attempt.data)
        max_test_count = int(form.max_test_count.data)
        selection_test_type = form.selection_test_type.data
        # other
        sampler = int(form.sampler.data)
        warm = int(form.warm.data)
        wait = int(form.wait.data)
        soft_test = form.soft_test.data
        hw_chsum = form.hw_chsum.data
        description = form.description.data
        # creates DB entry values
        trex_params = dict(
            duration=duration,
            traffic_pattern=traffic_pattern,
            multiplier=multiplier,
            sampler=sampler,
            warm=warm,
            wait=wait,
            soft_test=soft_test,
            hw_chsum=hw_chsum)
        rate_params = dict(
            accuracy=accuracy,
            rate=multiplier,
            rate_incr_step=rate_incr_step,
            max_succ_attempt=max_succ_attempt,
            max_test_count=max_test_count,
            test_type=selection_test_type)
        test_entr.name = name
        test_entr.test_type = test_type
        test_entr.description = description
        test_entr.parameters = dumps(dict(trex=trex_params) if test_type == 'common' else dict(trex=trex_params, rate=rate_params))
        # commit DB entry changes
        db.session.commit()
        # Success message
        msg = messages['success'].format('The test was changed')
        # showing form with success message
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # return clean form
    return render_template(
        'test_action.html',
        form=form,
        notes=notes,
        note=note,
        title=page_title,
        script_file=script_file,
        test_type=test_type,
        mode=mode)


@app.route('/test/new/stl/', methods=['GET', 'POST'])
def test_create_stl():
    mode = 'stateless'
    # getting test type list
    types = test_types
    list_types = [(test_type, test_type) for test_type in types[1:]]
    list_types.insert(0, (types[0], '{} (Default)'.format(types[0])))
    # getting test type list
    rate_types = stl_test_val['rate_types']  # in future 'cyclic', 'bundle'
    list_rate_types = [(rate_type, rate_type) for rate_type in rate_types[1:]]
    list_rate_types.insert(0, (rate_types[0], '{} (Default)'.format(rate_types[0])))
    # getting patterns list
    patterns = []
    lsdir = listdir(path=path.join(getcwd(), 'trex/test/stl/'))
    for item in lsdir:
        if item.endswith(('.yaml')):
            patterns.append(path.join('./trex/test/stl/', item))
    list_patterns = [(test_pattern, test_pattern) for test_pattern in patterns[1:]]
    list_patterns.insert(0, (patterns[0], '{} (Default)'.format(patterns[0])))
    # getting types of selection test
    selection_types = sel_test_types['all']
    list_selection_types = [(sel_type, sel_type) for sel_type in selection_types[1:]]
    list_selection_types.insert(0, (selection_types[0], '{} (Default)'.format(selection_types[0])))
    # getting lists of current tests values for checking
    curr_tests = models.Test.query.all()
    curr_name = []
    if len(curr_tests) > 0:
        for curr_test in curr_tests:
            curr_name.append(curr_test.name)

    class TestForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])])
        # general test params
        test_type = SelectField(
            label='Test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(types)],
            choices=list_types,
            default=types[0])
        rate_type = SelectField(
            label='Rate type',
            validators=[Required(), Length(min=1, max=128), AnyOf(rate_types)],
            choices=list_rate_types,
            default=rate_types[0])
        duration = IntegerField(
            label='Duration time in seconds',
            validators=[Required(), NumberRange(min=30, max=86400)],
            default=60)
        traffic_pattern = SelectField(
            label='Traffic pattern',
            validators=[Required(), Length(min=1, max=1024), AnyOf(patterns)],
            choices=list_patterns,
            default=patterns[0])
        rate = IntegerField(
            validators=[Required(), NumberRange(min=1, max=100000)],
            default=1000)
        sampler = IntegerField(
            label='Sampler time in seconds',
            validators=[Required(), NumberRange(min=1, max=600)],
            default=1)
        # selection test params
        accuracy = FloatField(
            label='Accuracy of test result in percents',
            validators=[Required(), NumberRange(min=0.0000000001, max=100)],
            default=0.1)
        rate_incr_step = IntegerField(
            label='Rate step',
            validators=[Required(), NumberRange(min=1, max=100000)],
            default=1000)
        max_succ_attempt = IntegerField(
            label='Maximum successful attemps for accepting result',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=3)
        max_test_count = IntegerField(
            label='Maximum number of test iterations',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=30)
        selection_test_type = SelectField(
            label='Selection test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(selection_types)],
            choices=list_selection_types,
            default=selection_types[0])
        # other parameters
        hw_chsum = BooleanField(label="Check if T-rex's NICs support HW offloading", default=False)
        description = TextAreaField(
            validators=[Length(max=1024)])
        # submit
        submit = SubmitField('Add new')
    # form
    form = TestForm()
    # variables
    page_title = 'New stateless test'
    script_file = 'tests.js'
    name = None
    test_type = types[0]
    rate_type = rate_types[0]
    duration = None
    traffic_pattern = None
    rate = None
    accuracy = None
    rate_incr_step = None
    max_succ_attempt = None
    max_test_count = None
    selection_test_type = None
    sampler = None
    hw_chsum = False
    description = ''
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    notes = stl_notes
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        form.name.data = None
        test_type = form.test_type.data
        form.test_type.data = None
        rate_type = form.rate_type.data
        form.rate_type.data = None
        duration = int(form.duration.data)
        form.duration.data = 60
        traffic_pattern = form.traffic_pattern.data
        form.traffic_pattern.data = ''
        rate = int(form.rate.data)
        form.rate.data = 1000
        # selection
        accuracy = (float(form.accuracy.data) / 100)
        form.accuracy.data = 0.1
        rate_incr_step = int(form.rate_incr_step.data)
        form.rate_incr_step.data = 1000
        max_succ_attempt = int(form.max_succ_attempt.data)
        form.max_succ_attempt.data = 3
        max_test_count = int(form.max_test_count.data)
        form.max_test_count.data = 30
        selection_test_type = form.selection_test_type.data
        form.selection_test_type.data = ''
        # other
        sampler = int(form.sampler.data)
        form.sampler.data = 1
        hw_chsum = form.hw_chsum.data
        form.hw_chsum.data = False
        description = form.description.data
        form.description.data = ''
        # creates DB entry
        trex_params = dict(
            duration=duration,
            traffic_pattern=traffic_pattern,
            rate=rate,
            rate_type=rate_type,
            sampler=sampler,
            hw_chsum=hw_chsum)
        rate_params = dict(
            accuracy=accuracy,
            rate=rate,
            rate_incr_step=rate_incr_step,
            max_succ_attempt=max_succ_attempt,
            max_test_count=max_test_count,
            test_type=selection_test_type)

        new_test = models.Test(
            name=name,
            mode=mode,
            test_type=test_type,
            description=description,
            hidden=False,
            parameters=dumps(dict(trex=trex_params) if test_type == 'common' else dict(trex=trex_params, rate=rate_params)))
        # adding DB entry in DB
        db.session.add(new_test)
        db.session.commit()
        # Success message
        msg = messages['success'].format('New test was added')
        # showing form with success message
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # return clean form
    return render_template(
        'test_action.html',
        form=form,
        notes=notes,
        note=note,
        title=page_title,
        script_file=script_file,
        test_type=test_type,
        mode=mode)


@app.route('/test/<int:test_id>/edit/stl/', methods=['GET', 'POST'])
def test_edit_stl(test_id):
    mode = 'stateless'
    test_entr = models.Test.query.get(test_id)
    # no task id return 404
    if not test_entr or test_entr.hidden:
        abort(404)
    elif test_entr.mode != mode:
        return redirect('/test/{}/edit/stf/'.format(test_id))
    # getting test type list
    types = test_types
    list_types = [(test_type, test_type) for test_type in types]
    types.remove(test_entr.test_type)
    types.insert(0, test_entr.test_type)

    test_papams_trex = loads(test_entr.parameters)['trex']
    # getting test type list
    rate_types = stl_test_val['rate_types']
    list_rate_types = [(rate_type, rate_type) for rate_type in rate_types]
    rate_types.remove(test_papams_trex['rate_type'])
    rate_types.insert(0, test_papams_trex['rate_type'])
    # getting patterns list
    patterns = []
    lsdir = listdir(path=path.join(getcwd(), 'trex/test/stl/'))
    for item in lsdir:
        if item.endswith(('.yaml')):
            patterns.append(path.join('./trex/test/stl/', item))
    list_patterns = [(test_pattern, test_pattern) for test_pattern in patterns]
    patterns.remove(test_papams_trex['traffic_pattern'])
    patterns.insert(0, test_papams_trex['traffic_pattern'])
    # getting rate params
    try:
        test_papams_rate = loads(test_entr.parameters)['rate']
    except KeyError:
        test_papams_rate = dict(
            accuracy=0.1,
            rate=1000,
            rate_incr_step=1000,
            max_succ_attempt=3,
            max_test_count=30,
            test_type='safe')
    # getting types of selection test
    selection_types = sel_test_types['all']
    list_selection_types = [(sel_type, sel_type) for sel_type in selection_types]
    selection_types.remove(test_papams_rate['test_type'])
    selection_types.insert(0, test_papams_rate['test_type'])
    # getting lists of current tests values for checking
    curr_tests = models.Test.query.filter(models.Test.id != test_id).all()
    print(curr_tests)
    curr_name = []
    if len(curr_tests) > 0:
        for curr_test in curr_tests:
            curr_name.append(curr_test.name)

    class TestForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])],
            default=test_entr.name)
        # general test params
        test_type = SelectField(
            label='Test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(types)],
            choices=list_types,
            default=types[0])
        rate_type = SelectField(
            label='Rate type',
            validators=[Required(), Length(min=1, max=128), AnyOf(rate_types)],
            choices=list_rate_types,
            default=rate_types[0])
        duration = IntegerField(
            label='Duration time in seconds',
            validators=[Required(), NumberRange(min=30, max=86400)],
            default=test_papams_trex['duration'])
        traffic_pattern = SelectField(
            label='Traffic pattern',
            validators=[Required(), Length(min=1, max=1024), AnyOf(patterns)],
            choices=list_patterns,
            default=patterns[0])
        rate = IntegerField(
            validators=[Required(), NumberRange(min=1, max=100000)],
            default=test_papams_trex['rate'])
        sampler = IntegerField(
            label='Sampler time in seconds',
            validators=[Required(), NumberRange(min=1, max=600)],
            default=test_papams_trex['sampler'])
        # selection test params
        accuracy = FloatField(
            label='Accuracy of test result in percents',
            validators=[Required(), NumberRange(min=0.0000000001, max=100)],
            default=test_papams_rate['accuracy'])
        rate_incr_step = IntegerField(
            label='Rate step',
            validators=[Required(), NumberRange(min=1, max=100000)],
            default=test_papams_rate['rate_incr_step'])
        max_succ_attempt = IntegerField(
            label='Maximum successful attemps for accepting result',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=test_papams_rate['max_succ_attempt'])
        max_test_count = IntegerField(
            label='Maximum number of test iterations',
            validators=[Required(), NumberRange(min=2, max=1000)],
            default=test_papams_rate['max_test_count'])
        selection_test_type = SelectField(
            label='Selection test type',
            validators=[Required(), Length(min=1, max=128), AnyOf(selection_types)],
            choices=list_selection_types,
            default=selection_types[0])
        # other parameters
        hw_chsum = BooleanField(label="Check if T-rex's NICs support HW offloading", default=test_papams_trex['hw_chsum'])
        description = TextAreaField(
            validators=[Length(max=1024)], default=test_entr.description)
        # submit
        submit = SubmitField('Save test')
    # form
    form = TestForm()
    # variables
    page_title = 'Edit stateless test {}'.format(test_entr.name)
    script_file = 'tests.js'
    name = None
    test_type = types[0]
    rate_type = rate_types[0]
    duration = None
    traffic_pattern = None
    rate = None
    accuracy = None
    rate_incr_step = None
    max_succ_attempt = None
    max_test_count = None
    selection_test_type = None
    sampler = None
    hw_chsum = False
    description = ''
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    notes = stl_notes
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        test_type = form.test_type.data
        rate_type = form.rate_type.data
        duration = int(form.duration.data)
        traffic_pattern = form.traffic_pattern.data
        rate = int(form.rate.data)
        # selection
        accuracy = (float(form.accuracy.data) / 100)
        rate_incr_step = int(form.rate_incr_step.data)
        max_succ_attempt = int(form.max_succ_attempt.data)
        max_test_count = int(form.max_test_count.data)
        selection_test_type = form.selection_test_type.data
        # other
        sampler = int(form.sampler.data)
        hw_chsum = form.hw_chsum.data
        description = form.description.data
        # creates DB entry values
        trex_params = dict(
            duration=duration,
            traffic_pattern=traffic_pattern,
            rate=rate,
            rate_type=rate_type,
            sampler=sampler,
            hw_chsum=hw_chsum)
        rate_params = dict(
            accuracy=accuracy,
            rate=rate,
            rate_incr_step=rate_incr_step,
            max_succ_attempt=max_succ_attempt,
            max_test_count=max_test_count,
            test_type=selection_test_type)
        test_entr.name = name
        test_entr.test_type = test_type
        test_entr.description = description
        test_entr.parameters = dumps(dict(trex=trex_params) if test_type == 'common' else dict(trex=trex_params, rate=rate_params))
        # commit DB entry changes
        db.session.commit()
        # Success message
        msg = messages['success'].format('The test was changed')
        # showing form with success message
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'test_action.html',
            form=form,
            notes=notes,
            note=note,
            title=page_title,
            script_file=script_file,
            msg=msg,
            test_type=test_type,
            mode=mode)
    # return clean form
    return render_template(
        'test_action.html',
        form=form,
        notes=notes,
        note=note,
        title=page_title,
        script_file=script_file,
        test_type=test_type,
        mode=mode)


@app.route('/test/<int:test_id>/')
def test_show(test_id, page=True):
    test_entr = models.Test.query.get(test_id)
    # no task id return 404
    if not page:
        if not test_entr:
            abort(404)
    else:
        if not test_entr or test_entr.hidden:
            abort(404)

    test_params_trex = loads(test_entr.parameters)['trex']
    try:
        test_papams_rate = loads(test_entr.parameters)['rate']
    except KeyError:
        test_papams_rate = False

    table_data = '''
        <tr>
            <td>Test name</td>
            <td>{name}</td>
        </tr>
        <tr>
            <td>T-rex test mode</td>
            <td>{mode}</td>
        </tr>
        <tr>
            <td>Test type</td>
            <td>{test_type}</td>
        </tr>
        <tr>
            <td>Description</td>
            <td>{description}</td>
        </tr>
        </table></div></div>'''.format(**test_entr['ALL_DICT'])

    table_items = {}
    # getting params db info
    table_items.update(test_params_trex)
    # rate/multiplier switcher
    if test_entr.mode == 'stateful':
        table_items['rate_label'] = 'Multiplier'
    else:
        table_items['rate_label'] = 'Rate'
    # rate/multiplier data
    if test_entr.mode == 'stateful':
        table_items['rate'] = table_items['multiplier']

    table_data += '''<div class="panel panel-default">
        <div class="panel-heading">Test details</div>
        <div class="table-responsive">
            <table class="table table-hover">
            <tr>
                <td>Duration</td>
                <td>{duration}</td>
            </tr>
            <tr>
                <td>Traffic pattern</td>
                <td>{traffic_pattern}</td>
            </tr>
            <tr>
                <td>{rate_label}</td>
                <td>{rate}</td>
            </tr>
            <tr>
                <td>Sampler</td>
                <td>{sampler}</td>
            </tr>'''.format(**table_items)

    if test_entr.mode == 'stateful':
        table_data += '''<tr>
                        <td>Warm time</td>
                        <td>{warm}</td>
                    </tr>
                    <tr>
                        <td>NIC initial delay time</td>
                        <td>{wait}</td>
                    </tr>
                    <tr>
                        <td>T-rex is VM</td>
                        <td>{soft_test}</td>
                    </tr>
                    <tr>
                        <td>T-rex supports HW offloading</td>
                        <td>{hw_chsum}</td>
                    </tr>
                    </table></div></div>'''.format(**test_params_trex)
    else:
        table_data += '''<tr>
                        <td>T-rex supports HW offloading</td>
                        <td>{hw_chsum}</td>
                    </tr>
                    </table></div></div>'''.format(**test_params_trex)
    if test_papams_rate:
        test_papams_rate['accuracy'] = test_papams_rate['accuracy'] * 100
        table_data += '''<div class="panel panel-default">
            <div class="panel-heading">Selection test details</div>
            <div class="table-responsive">
                <table class="table table-hover">
                <tr>
                    <td>Test accuracy</td>
                    <td>{accuracy}%</td>
                </tr>
                <tr>
                    <td>Rate increase step</td>
                    <td>{rate_incr_step}</td>
                </tr>
                <tr>
                    <td>Maximum successfull attempts</td>
                    <td>{max_succ_attempt}</td>
                </tr>
                <tr>
                    <td>Maximum number of test iterations</td>
                    <td>{max_test_count}</td>
                </tr>
                <tr>
                    <td>Test type</td>
                    <td>{test_type}</td>
                </tr>'''.format(**test_papams_rate)
    page_title = 'Details of test {}'.format(test_entr.name)
    if page:
        return render_template(
            'test.html',
            title=page_title,
            content=table_data)
    else:
        return table_data
