# different repeating values on pages, notes, etc


def humanize(data, units='si', end=''):
    # changed kilo/mega/giga/etc to K/M/G/etc; uses modulus, no "-"
    types = ('', '', 'K', 'M', 'G', 'P', 'E')
    if units == 'si':
        base = 1000
    else:
        base = 1024
    if abs(data) > base:
        for i in range(2, 6):
            if abs(data) < base ** i:
                return '{:.2f}{}{}'.format(abs(data) / (base ** (i - 1)), types[i], end)
                break
    else:
        return str(abs(data)) + ' ' + end


def list_to_seq_list(seq, output='num_list'):
    """ with output='seq_list' making list of lists with the same items; e.g. [1, 1, 3, 4, 4] ==> [[1, 1], [3], [4, 4]]
    with output='num_list' making list of lists with item and number of items in sequence; e.g. [1, 1, 3, 4, 4] ==> [[1, 2], [3, 1], [4, 2]]"""
    # previous initial must exactly be not the same as 1st sequence item
    previous = None if seq[0] is not None else 0
    seq_list = []
    # making list with items as sequence
    if output == 'seq_list':
        for item in seq:
            # if item is the same as last adds one to its sequence list
            if previous == item:
                seq_list[-1] += [item]
            # if item is not the same as last adds one to new sequence list
            else:
                seq_list.append([item])
            previous = item
    # making list with item and numder of current item in sequence
    elif output == 'num_list':
        counter = 0
        for item in seq:
            # if item is the same as last increased counter
            if previous == item:
                counter += 1
            # if item is not the same as last adds one to new sequence list; if counter more than 0 adds number of items to previous sequence list
            else:
                if counter != 0:
                    seq_list[-1] += [counter]
                counter = 1
                seq_list.append([item])
            previous = item
        # adding number of items to last sequence list
        seq_list[-1] += [counter]
    return seq_list


def no_db_item(item, item_type):
    # checking for DB entry returns False or error msg
    content = False
    # if no DB entry
    if len(item) < 1:
        # returns error msg for no item
        content = '<p class="lead">There was not any {0}. You should create {0} first.</p>'.format(item_type)
    return content


general_notes = {
    'table_req': 'All fields above are required',
}

test_types = ['common', 'selection']

# traffic patterns from cap2 directory on TRex
stf_traffic_patterns = [
    'cap2/dns.yaml',
    'cap2/dns_one_server.yaml',
    'cap2/http_simple.yaml',
    'cap2/http_short.yaml',
    'cap2/http_very_long.yaml',
    'cap2/imix_1518.yaml',
    'cap2/imix_64_100k.yaml',
    'cap2/imix_64_fast.yaml',
    'cap2/imix_64.yaml',
    'cap2/imix_9k.yaml',
    'cap2/imix_fast_1g_100k_flows.yaml',
    'cap2/imix_fast_1g.yaml',
    'cap2/imix.yaml',
    'cap2/ipv4_load_balance.yaml',
    'cap2/rtsp.yaml',
    'cap2/sfr2.yaml',
    'cap2/sfr3.yaml',
    'cap2/sfr.yaml',
    'cap2/short_tcp.yaml',
    'cap2/sip_short1.yaml',
    'cap2/sip_short2.yaml',
]

stf_notes = {
    'test': [
        '"Common" is simple test which executes one time',
        '"Selection" is test which is executed different number of time in order to reach result defined in parameters'
    ],
    'pattern': ['Test pattern which is executed on TRex (for some reason pattern must located on TRex now)'],
    'multiplier': ['Multiplier affects test pattern values (number of packets per second and packet flow gaps)'],
    'sampler': [
        'Sampler defines intervals for gathering and saving statistic during test. Every sampler interval statistic writes and in future one will be showed on chart (for some reason number of sampler size limited to 100 entries now, be careful choosing appropriate value)',
        'Set sampler to 0 for auto calculating sample value and solving situation with history size limit'
    ],
    'warm': ['Time for "warm" traffic which services for reasons like in case need to wait for some changes on network like tunnel upping, STP/dot1X timeouts, etc (migth not work on VM due some TRex soft nuances in current releases)'],
    'accuracy': ['Accuracy defines percent of per flow packet loss which can be accepted for passing test'],
    'rate_incr_step': ['Rate step value will be used for increasing/decreasing rate value in case test pass/not pass'],
    'selection_test_type': [
        'Defines which value will be used for checking test passing:',
        '"Safe" considers computed losses and TRex queue drop (strictest requirement for losses checking)',
        '"Accuracy" considers computed losses only (strict requirement for losses checking)',
        '"Drop" considers TRex queue drop/overload only (less strict requirement for losses checking)'
    ]
}

stl_notes = {
    'test': stf_notes['test'],
    'pattern': ['Test pattern which is executed on TRex'],
    'rate': ['Number of packets or bits per second'],
    'rate_type': ['Value for rate defines pps or bps rate will be used in test'],
    'sampler': [
        'Sampler defines intervals for gathering and saving statistic during test. Every sampler interval statistic writes and in future one will be showed on chart.',
        'Set sampler to 0 for auto calculating sample value.'
    ],
    'accuracy': stf_notes['accuracy'],
    'rate_incr_step': stf_notes['rate_incr_step'],
    'selection_test_type': stf_notes['selection_test_type'],
}

bundle_notes = {
    'test_list': ['Select test from list, if need specify number of selected test iteration. Iterations mean sequence from number of attempts for selected test. For some reason current number of test in bundle is limited (only 100 entries, 1 entry is 1 test iteration), in case total number of entries more than 100 only  100 will be used'],
    'randomize': ['After test is created, sequence of tests will be randomized'],
    'test_iter_random': ['Randomize number of iterations using "Number of iterations" value as random interval border. E.g. if value is 10, that means number of iterations will be from 1 to 10, if value is 25 then number will be from 1 to 25.']
}

stl_test_val = {
    'rate_types': ['pps', 'bps']
}

sel_test_types = {
    'all': ['safe', 'accuracy', 'drop']
}

validator_err = {
    'exist': 'Item already exists. For adding, change its value, please.'
}

tasks_statuses = {
    'all': ['done', 'pending', 'hold', 'testing', 'canceled', 'queued'],
    'gui_new': ['pending', 'hold'],
    'gui_edit': ['pending', 'hold', 'canceled']
}

trexes_statuses = {
    'all': ['idle', 'down', 'testing', 'error'],
    'gui': ['idle', 'down'],
}

devices_statuses = {
    'all': trexes_statuses['all'],
    'gui': trexes_statuses['gui'],
}

device_check_error = {'ip error', 'ping util permission denied', 'DNS resolve error'}

# labels
messages = {
    'success': '''
        <div class="alert alert-success alert-dismissible" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <strong>Success!</strong> {}
        </div>''',
    'no_succ': '''
        <div class="alert alert-danger alert-dismissible" role="alert">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <strong>Fail!</strong> {}
        </div>''',
    'succ_no_close': '<div class="alert alert-success" role="alert"><strong>Success!</strong> {}</div>',
    'succ_no_close_time': '<div class="alert alert-success" role="alert"><strong>Success!</strong> {0} Page is going to reload in <span id="timeout">{seconds}</span> seconds</div>',
    'no_succ_no_close': '<div class="alert alert-danger" role="alert"><strong>Fail!</strong> {}</div>',
    'warn_no_close': '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> {}</div>',
    'danger': '''
    <div class="alert alert-danger alert-dismissible" role="alert">
        <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <strong>Attention!</strong> {}
    </div>''',
    'warning': '''
    <div class="alert alert-danger alert-warning" role="alert">
        <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <strong>Warning!</strong> {}
    </div>''',
    'warn_no_close_time': '<div class="alert alert-warning" role="alert"><strong>Warning!</strong> {0} Need to wait for <span id="timeout">{seconds}</span> seconds</div>',
}

tasks_buttons = {
    'pending':
        '''<div class="btn-group btn-pending" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/hold" class="hold" id="{0}">On hold</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/cancel" class="cancel" id="{0}">Cancel</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'pending_hid':
        '''<div class="btn-group btn-pending hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/hold" class="hold" id="{0}">On hold</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/cancel" class="cancel" id="{0}">Cancel</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'hold':
        '''<div class="btn-group btn-hold" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/queue" class="queue" id="{0}">To queue</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/cancel" class="cancel" id="{0}">Cancel</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'hold_hid':
        '''<div class="btn-group btn-hold hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/queue" class="queue" id="{0}">To queue</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/cancel" class="cancel" id="{0}">Cancel</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'done':
        '''<div class="btn-group btn-done" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/readd" class="readd" id="{0}">Re add</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'done_hid':
        '''<div class="btn-group btn-done hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/readd" class="readd" id="{0}">Re add</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'canceled':
        '''<div class="btn-group btn-canceled" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/readd" class="readd" id="{0}">Re add</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'canceled_hid':
        '''<div class="btn-group btn-canceled hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/readd" class="readd" id="{0}">Re add</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'testing':
        '''<div class="btn-group btn-testing" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/kill" class="kill" id="{0}"><span class="text-danger">Force kill task</span></a></li>
            </ul>
        </div>''',
    'testing_hid':
        '''<div class="btn-group btn-testing hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/task/{0}/clone" class="clone" id="{0}">Clone task</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/kill" class="kill" id="{0}"><span class="text-danger">Force kill task</span></a></li>
            </ul>
        </div>''',
}

trexes_buttons = {
    'idle':
        '''<div class="btn-group btn-idle" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/down" class="down" id="{0}">Down TRex</a></li>
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'idle_hid':
        '''<div class="btn-group btn-idle hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/down" class="down" id="{0}">Down TRex</a></li>
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'down':
        '''<div class="btn-group btn-down" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/idle" class="idle" id="{0}">To idle</a></li>
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/trex/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'down_hid':
        '''<div class="btn-group btn-down hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/idle" class="idle" id="{0}">To idle</a></li>
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/task/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'testing':
        '''<div class="btn-group btn-testing" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
            </ul>
        </div>''',
    'testing_hid':
        '''<div class="btn-group btn-testing hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/trex/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
            </ul>
        </div>'''
}

devices_buttons = {
    'idle':
        '''<div class="btn-group btn-idle" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/device/{0}/down" class="down" id="{0}">Down device</a></li>
                <li><a href="/device/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'idle_hid':
        '''<div class="btn-group btn-idle hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/device/{0}/down" class="down" id="{0}">Down device</a></li>
                <li><a href="/device/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'down':
        '''<div class="btn-group btn-down" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/device/{0}/idle" class="idle" id="{0}">To idle</a></li>
                <li><a href="/device/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'down_hid':
        '''<div class="btn-group btn-down hidden" id="{0}">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
            <ul class="dropdown-menu">
                <li><a href="/device/{0}/idle" class="idle" id="{0}">To idle</a></li>
                <li><a href="/device/{0}/check" class="check" id="{0}"><span class="text-primary">Autoset status</span></a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/edit" class="edit" id="{0}">Edit</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/device/{0}/delete" class="delete" id="{0}">Delete</a></li>
            </ul>
        </div>''',
    'testing':
        '''<div class="btn-group btn-testing">
            <button type="button" class="btn btn-default dropdown-toggle " data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
        </div>''',
    'testing_hid':
        '''<div class="btn-group btn-testing hidden">
            <button type="button" class="btn btn-default dropdown-toggle " data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">Actions<span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
            </button>
        </div>'''
}
