# t-rex model page
from flask import render_template, abort
from app import app, db, models
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField, IntegerField, BooleanField
from wtforms.validators import Required, Length, AnyOf, Regexp, NumberRange, IPAddress, NoneOf, Optional
from app.helper import general_notes, validator_err


@app.route('/trexes/')
def tresex_table():
    page_title = 'T-rexes list'
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
        'check': '<li><a href="/trex/{0}/check" class="check" id="{0}">Autoset status</a></li>'
    }
    for entr in trexes_entr:
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
                <td>{hostname}</td>
                <td class="trex_status">{status}</td>
                <td>{ip4}</td>
                <td>{ip6}</td>
                <td>{fqdn}</td>
                <td>{port}</td>
                <td>{description}</td>
                <td>{vm_id}</td>
                <td>{host}</td>
                <td>{version}</td>
                <td>{1}</td>
                <td>{2}</td>
            </tr>
                '''.format(
                    status_row,
                    act_button.format(entr.id),
                    '<a href="/trex/{0}/tasks">Show</a>'.format(entr.id),
                    **entr['ALL_DICT'])

    return render_template('trexes.html', title=page_title, content=table_data, script_file=script_file)


@app.route('/trex/new/', methods=['GET', 'POST'])
def trex_create():
    # getting trex status list
    statuses = ['idle', 'down', 'error', 'testing']
    list_statuses = [(trex_status, trex_status) for trex_status in statuses[1:-2]]
    list_statuses.insert(0, (statuses[0], '{} (Default)'.format(statuses[0])))
    curr_trexes = models.Trex.query.all()
    curr_name = []
    curr_ip4 = []
    curr_ip6 = []
    curr_fqdn = []
    curr_vm_id = []
    if len(curr_trexes) > 0:
        for trex_entr in curr_trexes:
            curr_name.append(trex_entr.hostname)
            curr_ip4.append(trex_entr.ip4)
            curr_ip6.append(trex_entr.ip6)
            curr_fqdn.append(trex_entr.fqdn)
            curr_vm_id.append(trex_entr.vm_id)

    class TrexForm(FlaskForm):
        # making form
        hostname = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Hostname must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])])
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
        port = IntegerField(
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
        # general
        hostname = form.hostname.data
        form.hostname.data = None
        ip4 = form.ip4.data
        form.ip4.data = '127.0.0.1'
        ip6 = form.ip6.data
        form.ip6.data = '::1'
        fqdn = form.fqdn.data
        form.fqdn.data = None
        port = int(form.port.data)
        form.port.data = 8090
        vm_id = form.vm_id.data
        form.vm_id.data = None
        host = form.host.data
        form.host.data = None
        version = form.version.data
        form.version.data = None
        status = form.status.data
        form.status.data = status[0]
        description = form.description.data
        form.description.data = None

        # creates DB entr
        new_trex = models.Trex(
            hostname=hostname,
            ip4=ip4,
            ip6=ip6,
            fqdn=fqdn,
            port=port,
            vm_id=(vm_id if vm_id != '' else hostname),
            host=host,
            version=version,
            status=status,
            description=description)
        # adding DB entry in DB
        db.session.add(new_trex)
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> New t-rex was added</div>'
        # showing form with success message
        return render_template('trex_action.html', form=form, note=note, title=page_title, msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> <em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0])
        return render_template('trex_action.html', form=form, note=note, title=page_title, msg=msg)
    # return clean form
    return render_template('trex_action.html', form=form, note=note, title=page_title)


@app.route('/trex/<int:trex_id>/edit/', methods=['GET', 'POST'])
def trex_edit(trex_id):
    trex_entr = models.Trex.query.get(trex_id)

    # no task id return 404
    if not trex_entr:
        abort(404)

    # getting trex status list
    statuses = ['idle', 'down', 'error', 'testing']
    statuses.remove(trex_entr.status)
    statuses.insert(0, trex_entr.status)
    list_statuses = [(trex_status, trex_status) for trex_status in statuses]
    list_statuses.remove(('testing', 'testing'))
    list_statuses.remove(('error', 'error'))
    # getting lists of current trexes values for checking
    curr_trexes = models.Trex.query.filter(models.Trex.id != trex_id).all()
    curr_name = []
    curr_ip4 = []
    curr_ip6 = []
    curr_fqdn = []
    curr_vm_id = []
    if len(curr_trexes) > 0:
        for curr_trex in curr_trexes:
            curr_name.append(curr_trex.hostname)
            curr_ip4.append(curr_trex.ip4)
            curr_ip6.append(curr_trex.ip6)
            curr_fqdn.append(curr_trex.fqdn)
            curr_vm_id.append(curr_trex.vm_id)

    class TrexForm(FlaskForm):
        # making form
        hostname = StringField(
            validators=[Required(), Length(min=1, max=64), Regexp('^\w+$', message='Hostname must contain only letters numbers or underscore'), NoneOf(curr_name, message=validator_err['exist'])],
            default=trex_entr.hostname)
        ip4 = StringField(
            'IPv4 address',
            validators=[Required(), Length(min=7, max=15), IPAddress(message='Invalid IPv4 address'), NoneOf(curr_ip4, message=validator_err['exist'])],
            default=trex_entr.ip4)
        ip6 = StringField(
            'IPv6 address',
            validators=[Required(), Length(min=3, max=39), IPAddress(ipv6=True, message='Invalid IPv6 address'), NoneOf(curr_ip6, message=validator_err['exist'])],
            default=trex_entr.ip6)
        fqdn = StringField(
            'DNS name',
            validators=[Required(), Length(min=1, max=256), NoneOf(curr_fqdn, message=validator_err['exist'])],
            default=trex_entr.fqdn)
        port = IntegerField(
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
        hostname = form.hostname.data
        ip4 = form.ip4.data
        ip6 = form.ip6.data
        fqdn = form.fqdn.data
        port = int(form.port.data)
        vm_id = form.vm_id.data
        host = form.host.data
        version = form.version.data
        status = form.status.data
        description = form.description.data

        # creates DB entr
        trex_entr.hostname = hostname
        trex_entr.ip4 = ip4
        trex_entr.ip6 = ip6
        trex_entr.fqdn = fqdn
        trex_entr.port = port
        trex_entr.vm_id = (vm_id if vm_id != '' else hostname)
        trex_entr.host = host
        trex_entr.version = version
        trex_entr.status = status
        trex_entr.description = description
        # adding DB entry in DB
        db.session.commit()
        # Success message
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> t-rex {} was changed</div>'.format(trex_entr.hostname)
        # showing form with success message
        return render_template('trex_action.html', form=form, note=note, title=page_title, msg=msg)
    # if error occured
    if len(form.errors) > 0:
        msg = ''
        for err in form.errors:
            msg += '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> <em>{}</em>: {}</div>'.format(err.capitalize(), form.errors[err][0])
        return render_template('trex_action.html', form=form, note=note, title=page_title, msg=msg)
    # return clean form
    return render_template('trex_action.html', form=form, note=note, title=page_title)


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
        del_msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The t-rex {} was deleted</div>'.format(trex_entr.hostname)
        return render_template('delete.html', del_msg=del_msg, title=page_title)

    return render_template('delete.html', form=form, title=page_title)


@app.route('/trex/<int:trex_id>/down/')
def trex_hold(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    if trex_entr:
        trex_entr.status = 'down'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The t-rex  {} was changed to down</div>'.format(trex_entr.hostname)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The t-rex {} was not changed to down. No t-rex</div>'.format(trex_entr.hostname)
    return(msg)


@app.route('/trex/<int:trex_id>/idle/')
def trex_idle(trex_id):
    trex_entr = models.Trex.query.get(trex_id)
    if trex_entr:
        trex_entr.status = 'idle'
        # save DB entry in DB
        db.session.commit()
        msg = '<div class="alert alert-success" role="alert"><strong>Success!</strong> The t-rex  {} was changed to idled</div>'.format(trex_entr.hostname)
    else:
        msg = '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> The t-rex {} was not changed to idle. No t-rex</div>'.format(trex_entr.hostname)
    return(msg)
