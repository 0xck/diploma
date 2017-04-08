# DB main settings
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

# DB location
db_location = 'sqlite:///db.sqlite'

# choosing DB engine
db_engine = create_engine(db_location)
# making DB session and binding one with engine
db_session = scoped_session(sessionmaker(bind=db_engine))
# define DB type
DB = declarative_base()
# possibility to make queries to DB
DB.query = db_session.query_property()


# DB tables
class Trex(DB):
    # t-rex instance table
    __tablename__ = 'trex'
    # t-rex instance id
    id = Column(Integer, primary_key=True)
    # t-rex instance hostname
    hostname = Column(String(64), unique=True)
    # IPv4 mng address
    ip4 = Column(String(15), unique=True)
    # IPv6 mng address
    ip6 = Column(String(39), unique=True)
    # FQDN mng address
    fqdn = Column(String(256), unique=True)
    # t-rex instance port
    port = Column(Integer)
    # VM id
    vm_id = Column(String(64), unique=True)
    # hypervisor/cluster name
    host = Column(String(64))
    # t-rex instance type (statefull/stateless)
    mode = Column(String(9))
    # current t-rex status (down, idle, testing, etc)
    status = Column(String(64))
    # t-rex instance software version
    version = Column(String(8))
    # t-rex instance description
    description = Column(Text)
    # perhaps donfig info id needed which bind with test's task
    # ??? config = Column(String)

    def __init__(self, hostname=None, ip4=None, ip6=None, fqdn=None, port=None, vm_id=None, host=None, mode=None, status=None, version=None, description=None):
        self.hostname = hostname
        self.ip4 = ip4
        self.ip6 = ip6
        self.fqdn = fqdn
        self.port = port
        self.vm_id = vm_id
        self.host = host
        self.mode = mode
        self.status = status
        self.version = version
        self.description = description

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
        mode: {8},
        status: {9},
        version: {10},
        description: {11}'''.format(
            self.id,
            self.hostname,
            self.ip4,
            self.ip6,
            self.fqdn,
            self.port,
            self.vm_id,
            self.host,
            self.mode,
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
                self.mode,
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
                mode=self.mode,
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
                self.mode,
                self.status,
                self.version,
                self.description][index]


class Device(DB):
    # device table
    __tablename__ = 'device'
    # device id
    id = Column(Integer, primary_key=True)
    # device name
    name = Column(String(64), unique=True)
    # IPv4 mng address
    ip4 = Column(String(15), unique=True)
    # IPv6 mng address
    ip6 = Column(String(39), unique=True)
    # FQDN mng address
    fqdn = Column(String(256), unique=True)
    # device vendor
    vendor = Column(String(128))
    # device model
    model = Column(String(128))
    # current device status (down, idle, testing, etc)
    status = Column(String(64))
    # device firmware version
    firmware = Column(String(128))
    # device description
    description = Column(Text)
    # perhaps donfig info id needed which bind with test's task
    # ??? config = Column(String)

    def __init__(self, name=None, ip4=None, ip6=None, fqdn=None, vendor=None, model=None, status=None, firmware=None, description=None):
        self.name = name
        self.ip4 = ip4
        self.ip6 = ip6
        self.fqdn = fqdn
        self.vendor = vendor
        self.model = model
        self.status = status
        self.firmware = firmware
        self.description = description

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


if __name__ == "__main__":
    DB.metadata.create_all(bind=db_engine)
