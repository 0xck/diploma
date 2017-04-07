# t-rex instance DB part
from sqlalchemy import Column, Integer, String, Text
from db import DB


class Trex(DB):
    # t-rex instance table
    __tablename__ = 'trex'
    # t-rex id
    id = Column(Integer, primary_key=True)
    # t-rex instance hostname
    hostname = Column(String(64), unique=True)
    # IPv4 mng address
    ip4 = Column(String(15), unique=True)
    # IPv6 mng address
    ip6 = Column(String(39), unique=True)
    # FQDN mng address
    fqdn = Column(String(256), unique=True)
    # t-rex port
    port = Column(Integer)
    # VM id
    vm_id = Column(String(64), unique=True)
    # hypervisor/cluster name
    host = Column(String(64))
    # t-rex type (statefull/stateless)
    trex_type = Column(String(9))
    # current t-rex status (down, idle, testing, etc)
    status = Column(String(64))
    # t-rex version
    version = Column(String(8))
    # t-rex instance description
    description = Column(Text)
    # perhaps donfig info id needed which bind with test's task
    # ??? config = Column(String)

    def __init__(self, hostname=None, ip4=None, ip6=None, fqdn=None, port=None, vm_id=None, host=None, trex_type=None, status='None', version=None, description=None):
        self.hostname = hostname
        self.ip4 = ip4
        self.ip6 = ip6
        self.fqdn = fqdn
        self.port = port
        self.vm_id = vm_id
        self.host = host
        self.trex_type = trex_type
        self.status = status
        self.version = version
        self.description = description

    def __repr__(self):
        return '''
        id: {0},
        ip4: {1},
        ip6: {2},
        fqdn: {3},
        port: {4},
        vm_id: {5},
        host: {6},
        trex_type: {7},
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
            self.trex_type,
            self.status,
            self.version,
            self.description)
