<<<<<<< .merge_file_a06024
from flask import render_template, abort
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, IPAddress, NoneOf
from app.helper import general_notes, validator_err, messages, devices_statuses
=======
# flask
from flask import render_template, abort, jsonify
# DB
from app import app, db, models
# forms
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, IPAddress, NoneOf, Optional
# notes, statuses, etc
from app.helper import general_notes, validator_err, messages, devices_statuses
# autoset status
from checker import device_check
>>>>>>> .merge_file_a07892


@app.route('/devices/')
def devices_table(device_info=False, filter_nav=True):
<<<<<<< .merge_file_a06024
    page_title = 'Devices list'
    script_file = 'devices.js'
    if device_info:
        devices_entr = [device_info]
    else:
        devices_entr = models.Device.query.order_by(models.Device.id.desc()).all()
    table_data = ''
=======
    '''shows table of devices
    if device_info that means needs to return only specific devices, for task status page;
    filter_nav for showing tasks nav bar'''

    page_title = 'Devices list'
    # getting devices info
    # from list
    if device_info:
        devices_entr = [device_info]
    # from DB
    else:
        devices_entr = models.Device.query.order_by(models.Device.id.desc()).all()
    # var for future filling
    table_data = ''
    # action button template
>>>>>>> .merge_file_a07892
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
        'down': '<li><a href="/device/{0}/down" class="down" id="{0}">Down device</a></li>',
        'idle': '<li><a href="/device/{0}/idle" class="idle" id="{0}">To idle</a></li>',
<<<<<<< .merge_file_a06024
        'check': '<li><a href="/device/{0}/check" class="check" id="{0}">Autoset status</a></li>'
    }
    for entr in devices_entr:
        status_row = 'tr class="condition'
        if entr.status in {'idle', 'error'}:
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['separator'] + act_button_template['check'] + act_button_template['end']
=======
        'check': '<li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>'
    }
    # processing devices
    for entr in devices_entr:
        # checking status and sets html params for rows and buttons
        status_row = 'tr class="condition'
        if entr.status in {'idle', 'error'}:
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
>>>>>>> .merge_file_a07892
            if entr.status == 'error':
                status_row += ' danger error"'
            else:
                status_row += ' idle"'
        elif entr.status == 'down':
<<<<<<< .merge_file_a06024
            act_button = act_button_template['begin'] + act_button_template['idle'] + act_button_template['separator'] + act_button_template['check'] + act_button_template['end']
=======
            act_button = act_button_template['begin'] + act_button_template['idle'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
>>>>>>> .merge_file_a07892
            status_row += ' active down"'
        elif entr.status == 'testing':
            # unactiving button
            act_button = '''<div class="btn-group">
                        <button type="button" class="btn btn-default btn-xs dropdown-toggle " data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>'''
            status_row += ' warning testing"'
        # different errors
        else:
<<<<<<< .merge_file_a06024
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['separator'] + act_button_template['check'] + act_button_template['end']
            status_row += ' danger error"'
        table_items = {}
        table_items.update(entr['ALL_DICT'])
        table_items['status_row'] = status_row
        table_items['act_button'] = act_button.format(entr.id)
        table_items['show'] = '<a href="/tasks/device/{0}/">Show</a>'.format(entr.id)
=======
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
            status_row += ' danger error"'
        # gathering information for filling table
        table_items = {}
        # adding device db base info
        table_items.update(entr['ALL_DICT'])
        table_items['status_row'] = status_row
        # action button
        table_items['act_button'] = act_button.format(entr.id)
        # link for showing connected tasks
        table_items['show'] = '<a href="/tasks/device/{0}/">Show</a>'.format(entr.id)
        # making table row
>>>>>>> .merge_file_a07892
        table_data += '''
            <{status_row}>
                <td>{id}</td>
                <td>{name}</td>
                <td class="device_status">{status}</td>
                <td>{ip4}</td>
                <td>{ip6}</td>
                <td>{fqdn}</td>
                <td><small>{description}</small></td>
                <td>{vendor}</td>
                <td>{model}</td>
                <td>{firmware}</td>
                <td>{act_button}</td>
                <td>{show}</td>
            </tr>'''.format(**table_items)
<<<<<<< .merge_file_a06024
=======
    script_file = 'devices.js'
>>>>>>> .merge_file_a07892

    return render_template(
        'devices.html',
        title=page_title,
        content=table_data,
        script_file=script_file,
        filter_nav=filter_nav)


@app.route('/device/new/', methods=['GET', 'POST'])
def device_create():
<<<<<<< .merge_file_a06024
    # getting trex status list
    statuses = devices_statuses['all']
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
=======
    # making new device
    # getting info for filling forms in especial order
    # getting device status list
    statuses = devices_statuses['all']
    list_statuses = [(device_status, device_status) for device_status in statuses[1:-2]]
    list_statuses.insert(0, (statuses[0], '{} (Default)'.format(statuses[0])))
    # getting devices for filling name list
    curr_devices = models.Device.query.all()
    # making name list, needs for uniq device name
    if len(curr_devices) > 0:
        curr_names = [curr.name for curr in curr_devices]
    else:
        curr_names = []
>>>>>>> .merge_file_a07892

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
<<<<<<< .merge_file_a06024
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])])
        ip4 = StringField(
            'Management IPv4 address',
            validators=[Required(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address'), NoneOf(curr_ip4, message=validator_err['exist'])],
            default='127.0.0.1')
        ip6 = StringField(
            'Management IPv6 address',
            validators=[Required(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address'), NoneOf(curr_ip6, message=validator_err['exist'])],
            default='::1')
        fqdn = StringField(
            'Management DNS name',
            validators=[Required(), Length(min=1, max=256), NoneOf(curr_fqdn, message=validator_err['exist'])],
=======
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_names, message=validator_err['exist'])])
        ip4 = StringField(
            'Management IPv4 address',
            validators=[Optional(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address')],
            default='127.0.0.1')
        ip6 = StringField(
            'Management IPv6 address',
            validators=[Optional(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address')],
            default='::1')
        fqdn = StringField(
            'Management DNS name',
            validators=[Optional(), Length(min=1, max=256)],
>>>>>>> .merge_file_a07892
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
<<<<<<< .merge_file_a06024
    # form
=======
    # form obj
>>>>>>> .merge_file_a07892
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
<<<<<<< .merge_file_a06024
    # notes
=======
    # required note
>>>>>>> .merge_file_a07892
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
<<<<<<< .merge_file_a06024
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
=======
        # management data
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
        # management data was not defined
        if not ip4 and not ip6 and not fqdn:
            # warning message
            msg = messages['warn_no_close'].format('Any of management type (IPv4, IPv6, DNS name) has to be defined ')
            return render_template(
                'device_action.html',
                form=form, note=note,
                title=page_title,
                msg=msg)
        # other data
        name = form.name.data
        vendor = form.vendor.data
        model = form.model.data
        firmware = form.firmware.data
        status = form.status.data
        description = form.description.data
        # creates new DB entr
        new_device = models.Device(
            name=name,
            ip4=ip4 if ip4 != '' else None,
            ip6=ip6 if ip6 != '' else None,
            fqdn=fqdn if fqdn != '' else None,
>>>>>>> .merge_file_a07892
            vendor=vendor,
            model=model,
            firmware=firmware,
            status=status,
            description=description)
        # adding DB entry in DB
        db.session.add(new_device)
        db.session.commit()
        # Success message
        msg = messages['success'].format('New device was added')
<<<<<<< .merge_file_a06024
=======
        # cleaning form
        form.ip4.data = '127.0.0.1'
        form.ip6.data = '::1'
        form.fqdn.data = 'localhost'
        form.name.data = None
        form.vendor.data = None
        form.model.data = None
        form.firmware.data = None
        form.status.data = status[0]
        form.description.data = None
>>>>>>> .merge_file_a07892
        # showing form with success message
        return render_template(
            'device_action.html',
            form=form, note=note,
            title=page_title,
            msg=msg)
<<<<<<< .merge_file_a06024
    # if error occured
    if len(form.errors) > 0:
=======
    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
>>>>>>> .merge_file_a07892
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'device_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
<<<<<<< .merge_file_a06024
    # return clean form
=======

>>>>>>> .merge_file_a07892
    return render_template(
        'device_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/device/<int:device_id>/edit/', methods=['GET', 'POST'])
def device_edit(device_id):
<<<<<<< .merge_file_a06024
    device_entr = models.Device.query.get(device_id)
    # no task id return 404
    if not device_entr:
        abort(404)
=======
    # edits existing device
    device_entr = models.Device.query.get(device_id)
    # no device id returns 404
    if not device_entr:
        abort(404)
    # getting info for filling forms in especial order, fields will equal current device values
>>>>>>> .merge_file_a07892
    # getting trex status list
    statuses = devices_statuses['all']
    statuses.remove(device_entr.status)
    statuses.insert(0, device_entr.status)
    list_statuses = [(device_status, device_status) for device_status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('error', 'error'))
<<<<<<< .merge_file_a06024
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
=======
    # getting current devices
    curr_devices = models.Device.query.filter(models.Device.id != device_id).all()
    # making name list, needs for uniq device name
    if len(curr_devices) > 0:
        curr_names = [curr.name for curr in curr_devices]
    else:
        curr_names = []
>>>>>>> .merge_file_a07892

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
<<<<<<< .merge_file_a06024
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])],
            default=device_entr.name)
        ip4 = StringField(
            'Management IPv4 address',
            validators=[Required(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address'), NoneOf(curr_ip4, message=validator_err['exist'])],
            default=device_entr.ip4)
        ip6 = StringField(
            'Management IPv6 address',
            validators=[Required(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address'), NoneOf(curr_ip6, message=validator_err['exist'])],
            default=device_entr.ip6)
        fqdn = StringField(
            'Management DNS name',
            validators=[Required(), Length(min=1, max=256), NoneOf(curr_fqdn, message=validator_err['exist'])],
=======
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Name must contain only letters numbers or underscore'), NoneOf(curr_names, message=validator_err['exist'])],
            default=device_entr.name)
        ip4 = StringField(
            'Management IPv4 address',
            validators=[Optional(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address')],
            default=device_entr.ip4)
        ip6 = StringField(
            'Management IPv6 address',
            validators=[Optional(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address')],
            default=device_entr.ip6)
        fqdn = StringField(
            'Management DNS name',
            validators=[Optional(), Length(min=1, max=256)],
>>>>>>> .merge_file_a07892
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
<<<<<<< .merge_file_a06024
    # form
=======
    # form obj
>>>>>>> .merge_file_a07892
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
<<<<<<< .merge_file_a06024
    # notes
=======
    # require note
>>>>>>> .merge_file_a07892
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
<<<<<<< .merge_file_a06024
        # general
        name = form.name.data
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
=======
        # management data
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
        # management data was not defined
        if not ip4 and not ip6 and not fqdn:
            # Warning message
            msg = messages['warn_no_close'].format('Any of management type (IPv4, IPv6, DNS name) has to be defined ')
            return render_template(
                'device_action.html',
                form=form, note=note,
                title=page_title,
                msg=msg)
        # other data
        name = form.name.data
>>>>>>> .merge_file_a07892
        vendor = form.vendor.data
        model = form.model.data
        firmware = form.firmware.data
        status = form.status.data
        description = form.description.data
<<<<<<< .merge_file_a06024
        # creates DB entr
        device_entr.name = name
        device_entr.ip4 = ip4
        device_entr.ip6 = ip6
        device_entr.fqdn = fqdn
=======
        # changing DB entr
        device_entr.name = name
        device_entr.ip4 = ip4 if ip4 != '' else None
        device_entr.ip6 = ip6 if ip6 != '' else None
        device_entr.fqdn = fqdn if fqdn != '' else None
>>>>>>> .merge_file_a07892
        device_entr.vendor = vendor
        device_entr.model = model
        device_entr.firmware = firmware
        device_entr.status = status
        device_entr.description = description
        # adding DB entry in DB
        db.session.commit()
        # Success message
        msg = messages['success'].format('Device {} was changed'.format(device_entr.name))
        # showing form with success message
        return render_template(
            'device_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
<<<<<<< .merge_file_a06024
    # if error occured
    if len(form.errors) > 0:
=======
    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
>>>>>>> .merge_file_a07892
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'device_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
<<<<<<< .merge_file_a06024
    # return clean form
=======

>>>>>>> .merge_file_a07892
    return render_template(
        'device_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/device/<int:device_id>/delete/', methods=['GET', 'POST'])
def device_delete(device_id):
<<<<<<< .merge_file_a06024
    device_entr = models.Device.query.get(device_id)
    # no task id return 404
=======
    # deleting device from DB
    device_entr = models.Device.query.get(device_id)
    # no task id returns 404
>>>>>>> .merge_file_a07892
    if not device_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting device {}'.format(device_entr.name))
        submit = SubmitField('Delete device')
<<<<<<< .merge_file_a06024

    form = DeleteForm()
    page_title = 'Device {} deleting confirmation'.format(device_entr.name)

    if form.checker.data:
        form.checker.data = False
        db.session.delete(device_entr)
        db.session.commit()
=======
    # form obj
    form = DeleteForm()
    page_title = 'Device {} deleting confirmation'.format(device_entr.name)
    # checking if checked
    if form.checker.data:
        db.session.delete(device_entr)
        db.session.commit()
        # cleans form fields
        form.checker.data = False
>>>>>>> .merge_file_a07892
        del_msg = messages['succ_no_close'].format('The device {} was deleted'.format(device_entr.name))
        return render_template(
            'delete.html',
            del_msg=del_msg,
            title=page_title)

    return render_template(
        'delete.html',
        form=form,
        title=page_title)


@app.route('/device/<int:device_id>/down/')
def device_hold(device_id):
<<<<<<< .merge_file_a06024
    device_entr = models.Device.query.get(device_id)
=======
    # changing device status to down
    device_entr = models.Device.query.get(device_id)
    # changing status
>>>>>>> .merge_file_a07892
    if device_entr:
        device_entr.status = 'down'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The device {} was changed to down'.format(device_entr.name))
    else:
        msg = messages['no_succ'].format('The device {} was not changed to down. No device'.format(device_entr.name))
<<<<<<< .merge_file_a06024
    return(msg)
=======
    return msg
>>>>>>> .merge_file_a07892


@app.route('/device/<int:device_id>/idle/')
def device_idle(device_id):
<<<<<<< .merge_file_a06024
    device_entr = models.Device.query.get(device_id)
=======
    # changing device status to idle
    device_entr = models.Device.query.get(device_id)
    # changing status
>>>>>>> .merge_file_a07892
    if device_entr:
        device_entr.status = 'idle'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The device {} was changed to idle'.format(device_entr.name))
    else:
        msg = messages['no_succ'].format('The device {} was not changed to idle. No device'.format(device_entr.name))
<<<<<<< .merge_file_a06024
    return(msg)
=======
    return msg
>>>>>>> .merge_file_a07892


@app.route('/device/<int:device_id>')
def device_show(device_id):
<<<<<<< .merge_file_a06024
    device = models.Device.query.get(device_id)
    return devices_table(device_info=device, filter_nav=False)
=======
    # show device detail
    device = models.Device.query.get(device_id)
    return devices_table(device_info=device, filter_nav=False)


@app.route('/device/<int:device_id>/autoset/')
def device_autoset(device_id):
    # autosets status for device, only idle or down
    device = models.Device.query.get(device_id)
    # getting status
    if device:
        result = device_check(device)
        if result['state'] == 'idle':
            device.status = 'idle'
            msg_status = 'idle'
        elif result['state'] == 'unavailable':
            device.status = 'down'
            msg_status = 'down'
        # handles unknown value
        else:
            msg_status = 'unknown'
            msg = messages['no_succ'].format('The device {} status was not changed. Got unknown state'.format(device.name))
        # writes DB changes
        if msg_status != 'unknown':
            db.session.commit()
            msg = messages['success'].format('The device {} was changed to <label>{}</label>'.format(device.name, msg_status))
    else:
        msg = messages['no_succ'].format('The device {} status was not changed. No device'.format(device.name))
        msg_status = 'no_device'
    # return json for js handling
    return jsonify({'msg': msg, 'status': msg_status})
>>>>>>> .merge_file_a07892
