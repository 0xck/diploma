# t-rex model page
from flask import render_template, abort
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, IPAddress, NoneOf
from app.helper import general_notes, validator_err


@app.route('/devices/')
def devices_table():
    page_title = 'Devices list'
    script_file = 'devices.js'
    devices_entr = models.Device.query.order_by(models.Device.id.desc()).all()
    table_data = ''
    act_button_template = {
        'begin': '''<div class="btn-group">
                        <button type="button" class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">''',
        'end': '''<li><a href="/device/{0}/edit/" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/delete" class="delete" id="{0}">Delete</a></li>
                </ul>
            </div>''',
        'separator': '<li role="separator" class="divider"></li>',
        'down': '<li><a href="/device/{0}/down" class="down" id="{0}">Down T-rex</a></li>',
        'idle': '<li><a href="/device/{0}/idle" class="idle" id="{0}">To idle</a></li>',
        'check': '<li><a href="/device/{0}/check" class="check" id="{0}">Check status</a></li>'
    }
    for entr in devices_entr:
        status_row = 'tr'
        if entr.status in {'idle', 'error'}:
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['separator'] + act_button_template['check'] + act_button_template['end']
            if entr.status == 'error':
                status_row += ' class="danger"'
        elif entr.status == 'down':
            act_button = act_button_template['begin'] + act_button_template['idle'] + act_button_template['separator'] + act_button_template['check'] + act_button_template['end']
            status_row += ' class="active"'
        elif entr.status == 'testing':
            act_button = '''<div class="btn-group">
                        <button type="button" class="btn btn-default btn-xs dropdown-toggle " data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>'''
            status_row += ' class="warning"'
        table_data += '''
            <{0}>
                <td>{id}</td>
                <td>{name}</td>
                <td class="device_status">{status}</td>
                <td>{ip4}</td>
                <td>{ip6}</td>
                <td>{fqdn}</td>
                <td>{description}</td>
                <td>{vendor}</td>
                <td>{model}</td>
                <td>{firmware}</td>
                <td>{1}</td>
                <td>{2}</td>
            </tr>
                '''.format(
                        status_row,
                        act_button.format(entr.id),
                        '<a href="/device/{0}/tasks">Show</a>'.format(entr.id),
                        **entr['ALL_DICT'])

    return render_template('devices.html', title=page_title, content=table_data, script_file=script_file)


@app.route('/device/new/', methods=['GET', 'POST'])
def device_create():
    # getting trex status list
    statuses = ['idle', 'down', 'error', 'testing']
    list_statuses = [(device_status, device_status) for device_status in statuses[1:-2]]
    list_statuses.insert(0, (statuses[0], '{} (Default)'.format(statuses[0])))
    curr_trexes = models.Device.query.all()
    curr_name = []
    curr_ip4 = []
    curr_ip6 = []
    curr_fqdn = []
    if len(curr_trexes) > 0:
        for device_entr in curr_trexes:
            curr_name.append(device_entr.name)
            curr_ip4.append(device_entr.ip4)
            curr_ip6.append(device_entr.ip6)
            curr_fqdn.append(device_entr.fqdn)

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])])
        ip4 = StringField(
            'IPv4 address',
            validators=[Required(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address'), NoneOf(curr_ip4, message=validator_err['exist'])],
            default='127.0.0.1')
        ip6 = StringField(
            'IPv6 address',
            validators=[Required(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address'), NoneOf(curr_ip6, message=validator_err['exist'])],
            default='::1')
        fqdn = StringField(
            'DNS name',
            validators=[Required(), Length(min=1, max=256), NoneOf(curr_fqdn, message=validator_err['exist'])],
            default='localhost')
        vendor = StringField(
            'Device vendor',
            validators=[Length(max=128)])
        model = StringField(
            'Device model',
            validators=[Length(max=128)])
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        firmware = StringField(
            'Device firmware version',
            validators=[Length(max=128)])
        description = TextAreaField(
            validators=[Length(max=1024)])
        # submit
        submit = SubmitField('Add new')
    # form
    form = DeviceForm()
    # variables
    page_title = 'New Device'
    name = None
    ip4 = None
    ip6 = None
    fqdn = None
    vendor = None
    model = None
    status = None
    firmware = None
    description = None
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])

    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        form.name.data = None
        ip4 = form.ip4.data
        form.ip4.data = '127.0.0.1'
        ip6 = form.ip6.data
        form.ip6.data = '::1'
        fqdn = form.fqdn.data
        form.fqdn.data = None
        vendor = form.vendor.data
        form.vendor.data = None
        model = form.model.data
        form.model.data = None
        firmware = form.firmware.data
        form.firmware.data = None
        status = form.status.data
        form.status.data = status[0]
        description = form.description.data
        form.description.data = None

        # creates DB entr
        new_device = models.Device(
            name=name,
            ip4=ip4,
            ip6=ip6,
            fqdn=fqdn,
            vendor=vendor,
            model=model,
            firmware=firmware,
            status=status,
            description=description)
        # adding DB entry in DB
        db.session.add(new_device)
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> New device was added</div>'
        # showing form with success message
        return render_template('device_action.html', form=form, note=note, title=page_title, msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> <em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0])
        return render_template('device_action.html', form=form, note=note, title=page_title, msg=msg)
    # return clean form
    return render_template('device_action.html', form=form, note=note, title=page_title)


@app.route('/device/<int:device_id>/edit/', methods=['GET', 'POST'])
def device_edit(device_id):
    device_entr = models.Device.query.get(device_id)

    # no task id return 404
    if not device_entr:
        abort(404)

    # getting trex status list
    statuses = ['idle', 'down', 'error', 'testing']
    statuses.remove(device_entr.status)
    statuses.insert(0, device_entr.status)
    list_statuses = [(device_status, device_status) for device_status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('error', 'error'))
    # getting lists of current trexes values for checking
    curr_trexes = models.Device.query.filter(models.Device.id != device_id).all()
    curr_name = []
    curr_ip4 = []
    curr_ip6 = []
    curr_fqdn = []
    if len(curr_trexes) > 0:
        for curr_trex in curr_trexes:
            curr_name.append(curr_trex.name)
            curr_ip4.append(curr_trex.ip4)
            curr_ip6.append(curr_trex.ip6)
            curr_fqdn.append(curr_trex.fqdn)

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])],
            default=device_entr.name)
        ip4 = StringField(
            'IPv4 address',
            validators=[Required(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address'), NoneOf(curr_ip4, message=validator_err['exist'])],
            default=device_entr.ip4)
        ip6 = StringField(
            'IPv6 address',
            validators=[Required(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address'), NoneOf(curr_ip6, message=validator_err['exist'])],
            default=device_entr.ip6)
        fqdn = StringField(
            'DNS name',
            validators=[Required(), Length(min=1, max=256), NoneOf(curr_fqdn, message=validator_err['exist'])],
            default=device_entr.fqdn)
        vendor = StringField(
            'Device vendor',
            validators=[Length(max=128)],
            default=device_entr.vendor)
        model = StringField(
            'Device model',
            validators=[Length(max=128)],
            default=device_entr.model)
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        firmware = StringField(
            'Device firmware version',
            validators=[Length(max=128)],
            default=device_entr.firmware)
        description = TextAreaField(
            validators=[Length(max=1024)],
            default=device_entr.description)
        # submit
        submit = SubmitField('Save device')
    # form
    form = DeviceForm()
    # variables
    page_title = 'Edit device {}'.format(device_entr.name)
    name = None
    ip4 = None
    ip6 = None
    fqdn = None
    vendor = None
    model = None
    status = None
    firmware = None
    description = None
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])

    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        name = form.name.data
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
        vendor = form.vendor.data
        model = form.model.data
        firmware = form.firmware.data
        status = form.status.data
        description = form.description.data

        # creates DB entr
        device_entr.name = name
        device_entr.ip4 = ip4
        device_entr.ip6 = ip6
        device_entr.fqdn = fqdn
        device_entr.vendor = vendor
        device_entr.model = model
        device_entr.firmware = firmware
        device_entr.status = status
        device_entr.description = description
        # adding DB entry in DB
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> device {} was changed</div>'.format(device_entr.name)
        # showing form with success message
        return render_template('device_action.html', form=form, note=note, title=page_title, msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> <em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0])
        return render_template('device_action.html', form=form, note=note, title=page_title, msg=msg)
    # return clean form
    return render_template('device_action.html', form=form, note=note, title=page_title)


@app.route('/device/<int:device_id>/delete/', methods=['GET', 'POST'])
def device_delete(device_id):
    device_entr = models.Device.query.get(device_id)
    # no task id return 404
    if not device_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting device {}'.format(device_entr.name))
        submit = SubmitField('Delete device')

    form = DeleteForm()
    page_title = 'Device {} deleting confirmation'.format(device_entr.name)

    if form.checker.data:
        form.checker.data = False
        db.session.delete(device_entr)
        db.session.commit()
        del_msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The device {} was deleted</div>'.format(device_entr.name)
        return render_template('delete.html', del_msg=del_msg, title=page_title)

    return render_template('delete.html', form=form, title=page_title)


@app.route('/device/<int:device_id>/down/')
def device_hold(device_id):
    device_entr = models.Device.query.get(device_id)
    if device_entr:
        device_entr.status = 'down'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The device  {} was changed to down</div>'.format(device_entr.name)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The device {} was not changed to down. No t-rex</div>'.format(device_entr.name)
    return(msg)


@app.route('/device/<int:device_id>/idle/')
def device_idle(device_id):
    device_entr = models.Device.query.get(device_id)
    if device_entr:
        device_entr.status = 'idle'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The device  {} was changed to idled</div>'.format(device_entr.name)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The device {} was not changed to idle. No t-rex</div>'.format(device_entr.name)
    return(msg)
