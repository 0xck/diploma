# device pages
# flask
from flask import render_template, abort, jsonify
# DB
from app import app, db, models
# forms
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, IPAddress, NoneOf, Optional
# notes, statuses, etc
from app.helper import general_notes, validator_err, messages, devices_statuses, devices_buttons, device_check_error
# autoset status
from checker import device_check


@app.route('/devices/')
def devices_table(device_info=False, filter_nav=True):
    '''shows table of devices
    if device_info that means needs to return only certain devices, for task view page;
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
    # processing devices
    for entr in devices_entr:
        # checking status and sets html params for rows and buttons
        status_row = 'tr class="condition'
        if entr.status in {'idle', 'error'}:
            act_button = devices_buttons['idle'] + devices_buttons['down_hid'] + devices_buttons['testing_hid']
            if entr.status == 'error':
                status_row += ' danger error"'
            else:
                status_row += ' idle"'
        elif entr.status == 'down':
            act_button = devices_buttons['idle_hid'] + devices_buttons['down'] + devices_buttons['testing_hid']
            status_row += ' active down"'
        elif entr.status == 'testing':
            # unactiving button
            act_button = devices_buttons['idle_hid'] + devices_buttons['down_hid'] + devices_buttons['testing']
            status_row += ' warning testing"'
        # different errors
        else:
            act_button = devices_buttons['idle'] + devices_buttons['down_hid'] + devices_buttons['testing_hid']
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
    script_file = 'devices.js'

    return render_template(
        'devices.html',
        title=page_title,
        content=table_data,
        script_file=script_file,
        filter_nav=filter_nav)


@app.route('/device/new/', methods=['GET', 'POST'])
def device_create():
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

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
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
            validators=[Optional(), Length(min=1, max=256), Regexp('^[A-Za-z0-9_.-]+$', message='DNS name must contain only letters numbers, underscore, dot or dash')],
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
    # form obj
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
    # required note
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
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
        # showing form with success message
        return render_template(
            'device_action.html',
            form=form, note=note,
            title=page_title,
            msg=msg)
    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'device_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)

    return render_template(
        'device_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/device/<int:device_id>/edit/', methods=['GET', 'POST'])
def device_edit(device_id):
    # edits existing device
    device_entr = models.Device.query.get(device_id)
    # no device id returns 404
    if not device_entr:
        abort(404)
    # getting info for filling forms in especial order, fields will equal current device values
    # getting trex status list
    statuses = devices_statuses['all']
    statuses.remove(device_entr.status)
    statuses.insert(0, device_entr.status)
    list_statuses = [(device_status, device_status) for device_status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('error', 'error'))
    # getting current devices
    curr_devices = models.Device.query.filter(models.Device.id != device_id).all()
    # making name list, needs for uniq device name
    if len(curr_devices) > 0:
        curr_names = [curr.name for curr in curr_devices]
    else:
        curr_names = []

    class DeviceForm(FlaskForm):
        # making form
        name = StringField(
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
            validators=[Optional(), Length(min=1, max=256), Regexp('^[A-Za-z0-9_.-]+$', message='DNS name must contain only letters numbers, underscore, dot or dash')],
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
    # form obj
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
    # require note
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
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
        vendor = form.vendor.data
        model = form.model.data
        firmware = form.firmware.data
        status = form.status.data
        description = form.description.data
        # changing DB entr
        device_entr.name = name
        device_entr.ip4 = ip4 if ip4 != '' else None
        device_entr.ip6 = ip6 if ip6 != '' else None
        device_entr.fqdn = fqdn if fqdn != '' else None
        device_entr.vendor = vendor
        device_entr.model = model
        device_entr.firmware = firmware
        device_entr.status = status
        device_entr.description = description
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
    # if any error occured during validation process
    if len(form.errors) > 0:
        # showing error labels
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'device_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)

    return render_template(
        'device_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/device/<int:device_id>/delete/', methods=['GET', 'POST'])
def device_delete(device_id):
    # deleting device from DB
    device_entr = models.Device.query.get(device_id)
    # no task id returns 404
    if not device_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting device {}'.format(device_entr.name))
        submit = SubmitField('Delete device')
    # form obj
    form = DeleteForm()
    page_title = 'Device {} deleting confirmation'.format(device_entr.name)
    # checking if checked
    if form.checker.data:
        db.session.delete(device_entr)
        db.session.commit()
        # cleans form fields
        form.checker.data = False
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
    # changing device status to down
    device_entr = models.Device.query.get(device_id)
    # changing status
    if device_entr:
        device_entr.status = 'down'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The device {} was changed to down'.format(device_entr.name))
    else:
        msg = messages['no_succ'].format('The device {} was not changed to down. No device'.format(device_entr.name))
    return msg


@app.route('/device/<int:device_id>/idle/')
def device_idle(device_id):
    # changing device status to idle
    device_entr = models.Device.query.get(device_id)
    # changing status
    if device_entr:
        device_entr.status = 'idle'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The device {} was changed to idle'.format(device_entr.name))
    else:
        msg = messages['no_succ'].format('The device {} was not changed to idle. No device'.format(device_entr.name))
    return msg


@app.route('/device/<int:device_id>')
def device_show(device_id):
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
        elif result['state'] in device_check_error:
            msg_status = result['state']
            msg = messages['no_succ'].format('The device {} status was not changed. Got error "<label>{}</label>"'.format(device.name, msg_status))
        # handles unknown value
        else:
            msg_status = 'unknown'
            msg = messages['no_succ'].format('The device {} status was not changed. Got unknown state'.format(device.name))
        # writes DB changes
        if msg_status in {'idle', 'down'}:
            db.session.commit()
            msg = messages['success'].format('The device {} was changed to <label>{}</label>'.format(device.name, msg_status))
    else:
        msg = messages['no_succ'].format('The device {} status was not changed. No device'.format(device.name))
        msg_status = 'no_device'
    # return json for js handling
    return jsonify({'msg': msg, 'status': msg_status})
