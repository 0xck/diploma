from flask import render_template, abort, jsonify
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, IntegerField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, NumberRange, IPAddress, NoneOf, Optional
from app.helper import general_notes, validator_err, trexes_statuses, messages
from checker import trex_check


@app.route('/trexes/')
def trexes_table(trex_info=False, filter_nav=True):
    page_title = 'T-rexes list'
    if trex_info:
        trexes_entr = [trex_info]
    else:
        trexes_entr = models.Trex.query.order_by(models.Trex.id.desc()).all()
    script_file = 'trexes.js'
    table_data = ''
    act_button_template = {
        'begin': '''<div class="btn-group">
                        <button type="button" class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">''',
        'end': '''<li><a href="/trex/{0}/edit/" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/delete" class="delete" id="{0}">Delete</a></li>
                </ul>
            </div>''',
        'separator': '<li role="separator" class="divider"></li>',
        'down': '<li><a href="/trex/{0}/down" class="down" id="{0}">Down t-rex</a></li>',
        'idle': '<li><a href="/trex/{0}/idle" class="idle" id="{0}">To idle</a></li>',
        'check': '<li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>'
    }
    for entr in trexes_entr:
        status_row = 'tr class="condition'
        if entr.status in {'idle', 'error'}:
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
            if entr.status == 'error':
                status_row += ' danger error"'
            else:
                status_row += ' idle"'
        elif entr.status == 'down':
            act_button = act_button_template['begin'] + act_button_template['idle'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
            status_row += ' active down"'
        elif entr.status == 'testing':
            act_button = act_button_template['begin'] + act_button_template['check'] + '</ul>'
            status_row += ' warning testing"'
        # different errors
        else:
            act_button = act_button_template['begin'] + act_button_template['down'] + act_button_template['check'] + act_button_template['separator'] + act_button_template['end']
            status_row += ' danger error"'
        table_items = {}
        table_items.update(entr['ALL_DICT'])
        table_items['status_row'] = status_row
        table_items['act_button'] = act_button.format(entr.id)
        table_items['show'] = '<a href="/tasks/trex/{0}/">Show</a>'.format(entr.id)
        table_data += '''
            <{status_row}>
                <td>{id}</td>
                <td>{hostname}</td>
                <td class="trex_status">{status}</td>
                <td>{ip4}</td>
                <td>{ip6}</td>
                <td>{fqdn}</td>
                <td>{port}</td>
                <td><small>{description}</small></td>
                <td>{vm_id}</td>
                <td>{host}</td>
                <td>{version}</td>
                <td>{act_button}</td>
                <td>{show}</td>
            </tr>'''.format(**table_items)

    return render_template(
        'trexes.html',
        title=page_title,
        content=table_data,
        script_file=script_file,
        filter_nav=filter_nav)


@app.route('/trex/new/', methods=['GET', 'POST'])
def trex_create():
    # getting trex status list
    statuses = trexes_statuses['all']
    list_statuses = [(trex_status, trex_status) for trex_status in statuses[1:-2]]
    list_statuses.insert(0, (statuses[0], '{} (Default)'.format(statuses[0])))
    curr_trexes = models.Trex.query.all()
    if len(curr_trexes) > 0:
        curr_names = [curr.hostname for curr in curr_trexes]
        curr_vm_id = [curr.vm_id for curr in curr_trexes]
    else:
        curr_names = []
        curr_vm_id = []

    class TrexForm(FlaskForm):
        # making form
        hostname = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Hostname must contain only letters numbers or underscore'), NoneOf(curr_names, message=validator_err['exist'])])
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
            default='localhost')
        port = IntegerField(
            'T-rex daemon port',
            validators=[Required(), NumberRange(min=1, max=65535, message='Invalid port')],
            default=8090)
        vm_id = StringField(
            'VM ID',
            validators=[Length(max=64), Optional(), Regexp('^\w+$', message='VM ID must contain only letters numbers or underscore'), NoneOf(curr_vm_id, message=validator_err['exist'])])
        host = StringField(
            validators=[Length(max=64), Optional(), Regexp('^\w+$', message='Host must contain only letters numbers or underscore')])
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        version = StringField(
            'T-rex software version',
            validators=[Length(max=8)])
        description = TextAreaField(
            validators=[Length(max=1024)])
        # submit
        submit = SubmitField('Add new')
    # form
    form = TrexForm()
    # variables
    page_title = 'New T-rex'
    hostname = None
    ip4 = None
    ip6 = None
    fqdn = None
    port = None
    vm_id = None
    host = None
    status = None
    version = None
    description = None
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # management
        ip4 = form.ip4.data
        form.ip4.data = '127.0.0.1'
        ip6 = form.ip6.data
        form.ip6.data = '::1'
        fqdn = form.fqdn.data
        form.fqdn.data = None
        # management was not defined
        if not ip4 and not ip6 and not fqdn:
            # Warning message
            msg = messages['warn_no_close'].format('Any of management type (IPv4, IPv6, DNS name) has to be defined')
            return render_template(
                'trex_action.html',
                form=form, note=note,
                title=page_title,
                msg=msg)
        hostname = form.hostname.data
        vm_id = form.vm_id.data
        # checking vm id existing
        if vm_id == '':
            if hostname in curr_vm_id:
                msg = messages['warn_no_close'].format('VM ID {} aready exists'.format(vm_id))
                return render_template(
                    'trex_action.html',
                    form=form, note=note,
                    title=page_title,
                    msg=msg)
            else:
                vm_id = hostname
        port = int(form.port.data)
        host = form.host.data
        version = form.version.data
        status = form.status.data
        description = form.description.data
        # creates DB entr
        new_trex = models.Trex(
            hostname=hostname,
            ip4=ip4 if ip4 != '' else None,
            ip6=ip6 if ip6 != '' else None,
            fqdn=fqdn if fqdn != '' else None,
            port=port,
            vm_id=vm_id,
            host=host,
            version=version,
            status=status,
            description=description)
        # adding DB entry in DB
        db.session.add(new_trex)
        db.session.commit()
        # Success message
        msg = messages['success'].format('New t-rex was added')
        form.hostname.data = None
        form.vm_id.data = None
        form.ip4.data = '127.0.0.1'
        form.ip6.data = '::1'
        form.fqdn.data = 'localhost'
        form.port.data = 8090
        form.host.data = None
        form.version.data = None
        form.status.data = status[0]
        form.description.data = None
        # showing form with success message
        return render_template(
            'trex_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'trex_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
    # return clean form
    return render_template(
        'trex_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/trex/<int:trex_id>/edit/', methods=['GET', 'POST'])
def trex_edit(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    # no task id return 404
    if not trex_entr:
        abort(404)
    # getting trex status list
    statuses = trexes_statuses['all']
    statuses.remove(trex_entr.status)
    statuses.insert(0, trex_entr.status)
    list_statuses = [(trex_status, trex_status) for trex_status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('error', 'error'))
    # getting lists of current trexes values for checking
    curr_trexes = models.Trex.query.filter(models.Trex.id != trex_id).all()
    if len(curr_trexes) > 0:
        for curr_trex in curr_trexes:
            curr_names = [curr.hostname for curr in curr_trexes]
            curr_vm_id = [curr.vm_id for curr in curr_trexes]
        else:
            curr_names = []
            curr_vm_id = []

    class TrexForm(FlaskForm):
        # making form
        hostname = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Hostname must contain only letters numbers or underscore'), NoneOf(curr_names, message=validator_err['exist'])],
            default=trex_entr.hostname)
        ip4 = StringField(
            'Management IPv4 address',
            validators=[Optional(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address')],
            default=trex_entr.ip4)
        ip6 = StringField(
            'Management IPv6 address',
            validators=[Optional(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address')],
            default=trex_entr.ip6)
        fqdn = StringField(
            'Management DNS name',
            validators=[Optional(), Length(min=1, max=256)],
            default=trex_entr.fqdn)
        port = IntegerField(
            'T-rex daemon port',
            validators=[Required(), NumberRange(min=1, max=65535, message='Invalid port')],
            default=trex_entr.port)
        vm_id = StringField(
            'VM ID',
            validators=[Length(max=64), Optional(), Regexp('^\w+$', message='VM ID must contain only letters numbers or underscore'), NoneOf(curr_vm_id, message=validator_err['exist'])],
            default=trex_entr.vm_id)
        host = StringField(
            validators=[Length(max=64), Optional(), Regexp('^\w+$', message='Host must contain only letters numbers or underscore')],
            default=trex_entr.host)
        status = SelectField(
            validators=[Required(), Length(min=1, max=64), AnyOf(statuses)],
            choices=list_statuses,
            default=statuses[0])
        version = StringField(
            'T-rex software version',
            validators=[Length(max=8)],
            default=trex_entr.version)
        description = TextAreaField(
            validators=[Length(max=1024)],
            default=trex_entr.description)
        # submit
        submit = SubmitField('Save t-rex')
    # form
    form = TrexForm()
    # variables
    page_title = 'Edit T-rex {}'.format(trex_entr.hostname)
    hostname = None
    ip4 = None
    ip6 = None
    fqdn = None
    port = None
    vm_id = None
    host = None
    status = None
    version = None
    description = None
    # notes
    note = '<p class="help-block">Note. {}<p>'.format(general_notes['table_req'])
    # checking if submit or submit without errors
    if form.validate_on_submit():
        # defining variables value from submitted form
        # general
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
        # management was not defined
        if not ip4 and not ip6 and not fqdn:
            # Warning message
            msg = messages['warn_no_close'].format('Any of management type (IPv4, IPv6, DNS name) has to be defined ')
            return render_template(
                'trex_action.html',
                form=form, note=note,
                title=page_title,
                msg=msg)
        hostname = form.hostname.data
        vm_id = form.vm_id.data
        # checking vm id existing
        if vm_id == '':
            if hostname in curr_vm_id:
                msg = messages['warn_no_close'].format('VM ID {} aready exists'.format(vm_id))
                return render_template(
                    'trex_action.html',
                    form=form, note=note,
                    title=page_title,
                    msg=msg)
            else:
                vm_id = hostname
        port = int(form.port.data)
        host = form.host.data
        version = form.version.data
        status = form.status.data
        description = form.description.data
        # creates DB entr
        trex_entr.hostname = hostname
        trex_entr.ip4 = ip4 if ip4 != '' else None
        trex_entr.ip6 = ip6 if ip6 != '' else None
        trex_entr.fqdn = fqdn if fqdn != '' else None
        trex_entr.port = port
        trex_entr.vm_id = (vm_id if vm_id != '' else hostname)
        trex_entr.host = host
        trex_entr.version = version
        trex_entr.status = status
        trex_entr.description = description
        # adding DB entry in DB
        db.session.commit()
        # Success message
        msg = messages['succ_no_close'].format('t-rex {} was changed'.format(trex_entr.hostname))
        # showing form with success message
        return render_template(
            'trex_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += messages['warn_no_close'].format('<em>{}</em>: {}'.format(err.capitalize(), form.errors[err][0]))
        return render_template(
            'trex_action.html',
            form=form,
            note=note,
            title=page_title,
            msg=msg)
    # return clean form
    return render_template(
        'trex_action.html',
        form=form,
        note=note,
        title=page_title)


@app.route('/trex/<int:trex_id>/delete/', methods=['GET', 'POST'])
def trex_delete(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    # no task id return 404
    if not trex_entr:
        abort(404)

    class DeleteForm(FlaskForm):
        # making form
        checker = BooleanField(label='Check for deleting t-rex {}'.format(trex_entr.hostname))
        submit = SubmitField('Delete t-rex')

    form = DeleteForm()
    page_title = 'T-rex {} deleting confirmation'.format(trex_entr.hostname)

    if form.checker.data:
        form.checker.data = False
        db.session.delete(trex_entr)
        db.session.commit()
        del_msg = messages['succ_no_close'].format('The t-rex {} was deleted</div>'.format(trex_entr.hostname))
        return render_template(
            'delete.html',
            del_msg=del_msg,
            title=page_title)

    return render_template('delete.html', form=form, title=page_title)


@app.route('/trex/<int:trex_id>/down/')
def trex_hold(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    if trex_entr:
        trex_entr.status = 'down'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The t-rex {} was changed to down'.format(trex_entr.hostname))
    else:
        msg = messages['no_succ'].format('The t-rex {} was not changed to down. No t-rex'.format(trex_entr.hostname))
    return(msg)


@app.route('/trex/<int:trex_id>/idle/')
def trex_idle(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    if trex_entr:
        trex_entr.status = 'idle'
        # save DB entry in DB
        db.session.commit()
        msg = messages['success'].format('The t-rex {} was changed to idle'.format(trex_entr.hostname))
    else:
        msg = messages['no_succ'].format('The t-rex {} was not changed to idle. No t-rex'.format(trex_entr.hostname))
    return(msg)


@app.route('/trex/<int:trex_id>/')
def trex_show(trex_id):
    trex = models.Trex.query.get(trex_id)
    return trexes_table(trex_info=trex, filter_nav=False)


@app.route('/trex/<int:trex_id>/autoset/')
def trex_autoset(trex_id):
    trex = models.Trex.query.get(trex_id)
    if trex:
        result = trex_check(trex)
        if result['state'] == 'idle':
            trex.status = 'idle'
            msg_status = 'idle'
        elif result['state'] == 'unavailable':
            trex.status = 'down'
            msg_status = 'down'
        elif result['state'] == 'running' or result['state'] == 'stateless':
            trex.status = 'testing'
            msg_status = 'testing'
        elif result['state'] == 'error_rpc':
            trex.status = 'error_rpc'
            msg_status = 'error_rpc'
        else:
            msg_status = 'unknown'
            msg = messages['no_succ'].format('The t-rex {} status was not changed. Got unknown state'.format(trex.hostname))
        if msg_status != 'unknown':
            db.session.commit()
            msg = messages['success'].format('The t-rex {} was changed to <label>{}</label>'.format(trex.hostname, msg_status))
    else:
        msg = messages['no_succ'].format('The t-rex {} status was not changed. No t-rex'.format(trex.hostname))
        msg_status = 'no_trex'
    return jsonify({'msg': msg, 'status': msg_status})
