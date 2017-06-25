# models for working with DB
# DB
from app import db
from json import loads


# db tables
class Trex(db.Model):
    # t-rex instance table
    __tablename__ = 'trex'
    # t-rex instance id
    id = db.Column(db.Integer, primary_key=True)
    # t-rex instance hostname
    hostname = db.Column(db.String(64), unique=True)
    # IPv4 mng address
    ip4 = db.Column(db.String(15), nullable=True)
    # IPv6 mng address
    ip6 = db.Column(db.String(39), nullable=True)
    # FQDN mng address
    fqdn = db.Column(db.String(256), nullable=True)
    # t-rex instance port
    port = db.Column(db.Integer)
    # VM id
    vm_id = db.Column(db.String(64), unique=True)
    # hypervisor/cluster name
    host = db.Column(db.String(64))
    # current t-rex status (down, idle, testing, etc)
    status = db.Column(db.String(64))
    # t-rex instance software version
    version = db.Column(db.String(8))
    # t-rex instance description
    description = db.Column(db.Text)
    # associated tasks
    tasks = db.relationship('Task', backref='trexes')

    def __repr__(self):
        return '''
        id: {0},
        hostname: {1},
        ip4: {2}
        ip6: {3},
        fqdn: {4},
        port: {5},
        vm_id: {6},
        host: {7},
        status: {8},
        version: {9},
        description: {10}'''.format(
            self.id,
            self.hostname,
            self.ip4,
            self.ip6,
            self.fqdn,
            self.port,
            self.vm_id,
            self.host,
            self.status,
            self.version,
            self.description)

    def __getitem__(self, index):
        # different returns
        # return list of args
        if index == 'ALL_LIST':
            return [
                self.id,
                self.hostname,
                self.ip4,
                self.ip6,
                self.fqdn,
                self.port,
                self.vm_id,
                self.host,
                self.status,
                self.version,
                self.description]
        # return dict of args
        elif index == 'ALL_DICT':
            return dict(
                id=self.id,
                hostname=self.hostname,
                ip4=self.ip4,
                ip6=self.ip6,
                fqdn=self.fqdn,
                port=self.port,
                vm_id=self.vm_id,
                host=self.host,
                status=self.status,
                version=self.version,
                description=self.description)
        # return index of list of args
        else:
            return [
                self.id,
                self.hostname,
                self.ip4,
                self.ip6,
                self.fqdn,
                self.port,
                self.vm_id,
                self.host,
                self.status,
                self.version,
                self.description][index]


class Device(db.Model):
    # device table
    __tablename__ = 'device'
    # device id
    id = db.Column(db.Integer, primary_key=True)
    # device name
    name = db.Column(db.String(64))
    # IPv4 mng address
    ip4 = db.Column(db.String(15), nullable=True)
    # IPv6 mng address
    ip6 = db.Column(db.String(39), nullable=True)
    # FQDN mng address
    fqdn = db.Column(db.String(256), nullable=True)
    # device vendor
    vendor = db.Column(db.String(128))
    # device model
    model = db.Column(db.String(128))
    # current device status (down, idle, testing, etc)
    status = db.Column(db.String(64))
    # device firmware version
    firmware = db.Column(db.String(128))
    # device description
    description = db.Column(db.Text)
    # associated tasks
    tasks = db.relationship('Task', backref='devices')

    def __repr__(self):
        return '''
        id: {0},
        name: {1}
        ip4: {2},
        ip6: {3},
        fqdn: {4},
        vendor: {5}
        model: {6},
        status: {7},
        firmware: {8},
        description: {9}'''.format(
            self.id,
            self.name,
            self.ip4,
            self.ip6,
            self.fqdn,
            self.vendor,
            self.model,
            self.status,
            self.firmware,
            self.description)

    def __getitem__(self, index):
        # different returns
        # return list of args
        if index == 'ALL_LIST':
            return [
                self.id,
                self.name,
                self.ip4,
                self.ip6,
                self.fqdn,
                self.vendor,
                self.model,
                self.status,
                self.firmware,
                self.description]
        # return dict of args
        elif index == 'ALL_DICT':
            return dict(
                id=self.id,
                name=self.name,
                ip4=self.ip4,
                ip6=self.ip6,
                fqdn=self.fqdn,
                vendor=self.vendor,
                model=self.model,
                status=self.status,
                firmware=self.firmware,
                description=self.description)
        # return index of list of args
        else:
            return [
                self.id,
                self.name,
                self.ip4,
                self.ip6,
                self.fqdn,
                self.vendor,
                self.model,
                self.status,
                self.firmware,
                self.description][index]


class Task(db.Model):
    # tasks table
    __tablename__ = 'task'
    # task id
    id = db.Column(db.Integer, primary_key=True)
    # task description
    description = db.Column(db.Text)
    # task start time+date
    start_time = db.Column(db.DateTime, nullable=True)
    # task start time+date
    end_time = db.Column(db.DateTime, nullable=True)
    # current task status (pending, testing, done)
    status = db.Column(db.String(64))
    # result with short description (pending, success, error, canceled)
    result = db.Column(db.String(64), nullable=True)
    # result data
    data = db.Column(db.Text, nullable=True)
    # associated trex instance
    trex = db.Column(db.Integer, db.ForeignKey('trex.hostname'))
    # associated device
    device = db.Column(db.Integer, db.ForeignKey('device.name'), nullable=True)
    # associated test
    test = db.Column(db.Integer, db.ForeignKey('test.name'))
    # associated test data
    test_data = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '''
        id: {},
        description: {},
        start_time: {},
        end_time: {}
        status: {},
        result: {},
        trex: {},
        device: {},
        test: {},
        data: {}
        '''.format(
            self.id,
            self.description,
            self.start_time,
            self.end_time,
            self.status,
            self.result,
            self.trex,
            self.device,
            self.test,
            self.data)

    def __getitem__(self, index):
        # different returns
        # return list of args
        if index == 'ALL_LIST':
            return [
                self.id,
                self.description,
                self.start_time,
                self.end_time,
                self.status,
                self.result,
                self.trex,
                self.device,
                self.test,
                self.data]
        # return dict of args
        elif index == 'ALL_DICT':
            return dict(
                id=self.id,
                description=self.description,
                start_time=self.start_time,
                end_time=self.end_time,
                status=self.status,
                result=self.result,
                trex=self.trex,
                device=self.device,
                test=self.test,
                data=self.data)
        # return index of list of args
        else:
            return [
                self.id,
                self.description,
                self.start_time,
                self.end_time,
                self.status,
                self.result,
                self.trex,
                self.device,
                self.test,
                self.data][index]


class Test(db.Model):
    # test table
    __tablename__ = 'test'
    # test id
    id = db.Column(db.Integer, primary_key=True)
    # test name
    name = db.Column(db.String(64), unique=True)
    # trex instance test mode statefull/stateless
    mode = db.Column(db.String(9))
    # test type (common, selection)
    test_type = db.Column(db.String(128))
    # test attributes like patterns, variables, patametrs etc
    parameters = db.Column(db.Text)
    # test description
    description = db.Column(db.Text)
    # associated trex instance
    tasks = db.relationship('Task', backref='tests')

    def __repr__(self):
        return '''
        id: {0},
        name: {1}
        mode: {2},
        test_type: {3},
        parameters: {4},
        description: {5}
        '''.format(
            self.id,
            self.name,
            self.mode,
            self.test_type,
            self.parameters,
            self.description)

    def __getitem__(self, index):
        # different returns
        # return list of args
        if index == 'ALL_LIST':
            return [
                self.id,
                self.name,
                self.mode,
                self.test_type,
                self.description,
                self.parameters]
        # return dict of args
        elif index == 'ALL_DICT':
            return dict(
                id=self.id,
                name=self.name,
                mode=self.mode,
                test_type=self.test_type,
                description=self.description,
                parameters=self.parameters)
        # return dict of args
        elif index == 'ALL_DICT_NO_JSON':
            return dict(
                id=self.id,
                name=self.name,
                mode=self.mode,
                test_type=self.test_type,
                description=self.description,
                parameters=loads(self.parameters))
        # return index of list of args
        else:
            return [
                self.id,
                self.name,
                self.mode,
                self.test_type,
                self.description,
                self.parameters][index]
