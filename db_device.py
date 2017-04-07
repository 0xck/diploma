# device DB part
from sqlalchemy import Column, Integer, String, Text
from db import DB


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

    def __init__(self, name=None, ip4=None, ip6=None, fqdn=None, model=None, status=None, firmware=None, description=None):
        self.name = name
        self.ip4 = ip4
        self.ip6 = ip6
        self.fqdn = fqdn
        self.model = model
        self.status = status
        self.firmware = firmware
        self.description = description

    def __repr__(self):
        return '''
        id: {0},
        ip4: {1},
        ip6: {2},
        fqdn: {3},
        model: {4},
        status: {5},
        firmware: {6},
        description: {7}'''.format(
            self.id,
            self.name,
            self.ip4,
            self.ip6,
            self.fqdn,
            self.model,
            self.status,
            self.firmware,
            self.description)
