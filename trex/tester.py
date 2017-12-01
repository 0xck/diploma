"""
tester for making test with trex client
"""
import logging
from enum import Enum, unique
from .helper import Result, TREXMODE, TREXSTATUS, TypeProperty, ValueProperty, firstfilter, TREXRESERV
from .exceptions import TesterError, SolverError, TRexClientWrapperError, TRexSTLClientWrapperError
from .client import TRexClientWrapper, TRexSTLClientWrapper
from .solvers.common import solver

# generic trex server settings
SERVER_DEFAULT = dict(
    trex_host='localhost',
    trex_daemon_port=8090,
    master_daemon_port=8091,
    trex_zmq_port=4500,
    timeout=5,
    # max history size
    max_history_size=100)

# generic trex server settings for stl mode
STL_DEFAULT = dict(
    server=SERVER_DEFAULT['trex_host'],
    sync_port=4501,
    async_port=4500)

# generic trex test settings
STF_TEST_DEFAULT = dict(
    # trex local config file
    cfg='/etc/trex_cfg.yaml',
    # test duration
    d=60,
    # multiplier
    m=1,
    # test pattern local file
    f='',
    # latency checking packet number, if 0 latency test is disabled
    l=0,
    # traffic warm up time
    k=30,
    # work as software appliance
    software=True,
    # timeout before init interfacesand send traffic
    w=1,
    # IPv6 support
    ipv6=False,
    # HW checksumm offloading
    checksum_offload_disable=False,
    # HW TSO offloading
    tso_disable=False,
    # only latency test disable
    lo=False)

STL_TEST_DEFAULT = dict(
    # user for trex operation
    # user='trex',
    # test pattern local file; only YAML now,
    # because need to figure out issue with py import, get class error there
    pattern='',
    # flow arguments
    # t-rex interfaces
    ifaces=[0, 1],
    # interface for active flow
    act_iface=0,
    # rate type PPS or BPS
    rate_type='pps',
    # number of pakets or bits
    rate=1000,
    # duration
    duration=60,
    # ARP retries
    arp_retries=0,
    # traffic warm up time
    warm=10)


@unique
class CHECKMODE(Enum):

    fast = 'fast'
    full = 'full'
    custom = 'custom'


class Tester():

    server = TypeProperty('server', TRexClientWrapper)
    mode = ValueProperty('mode', TREXMODE)
    client = TypeProperty('client', (TRexClientWrapper, TRexSTLClientWrapper))

    @staticmethod
    def config_trex_server(config):

        cfg = SERVER_DEFAULT
        if config:
            cfg.update({k: v for k, v in config.items() if k in cfg})

        return cfg

    @staticmethod
    def test_config_stf(config):

        cfg = STF_TEST_DEFAULT
        if config:
            cfg.update(config)

        return cfg

    @staticmethod
    def config_stl_client(config):

        # stl client config
        cfg = STL_DEFAULT
        if config:
            cfg.update({k: v for k, v in config.items() if k in cfg})

        return cfg

    @staticmethod
    def test_config_stl(config):

        # test config
        cfg = STL_TEST_DEFAULT
        if config:
            cfg.update(config)

        return cfg

    @staticmethod
    def get_stf(config, sampler=1, test=None):

        return TRexClientWrapper(config, test, sampler)

    @staticmethod
    def get_stl(trex, client, test, sampler):

        return TRexSTLClientWrapper(trex, client, test, sampler)

    def __init__(self, server=None, mode=None, test=None, sampler=1, **kwargs):
        """
        """

        template = 'An error occured during init test parameters: "{}"'.format

        try:
            # getting trex mode
            self.mode = firstfilter(lambda m: m.value == mode, TREXMODE)
            # getting mng client for trex server
            server_cfg = self.config_trex_server(server)
            self.server = self.get_stf(server_cfg)
            """
            getting test client settings:
                stf client obj (TRexClientWrapper):
                    server config (dict)
                    test config (dict)
                    sampler (int)
                stl client obj (TRexSTLClientWrapper):
                    trex server client (TRexClientWrapper)
                    stl client config (dict)
                    test config (dict)
                    sampler (int)
            """
            if self.mode == TREXMODE.stf:
                self.client = self.get_stf(server_cfg, sampler=sampler, test=self.test_config_stf(test))
            else:
                self.client = self.get_stl(self.server, self.config_stl_client(test), self.test_config_stl(test), sampler)

        except (TRexClientWrapperError, TRexSTLClientWrapperError) as err:
            logging.error(template(err.message))
            raise TesterError(err.message, **err.get_kwargs())

        except (TypeError, ValueError) as err:
            content = [type(err), err.args]
            logging.error(template(content))
            raise TesterError('Wrong value in given settings', content=content)

    def _check_idle(self, result):
        # return error if trex is not available

        return result if result.value == TREXSTATUS.idle else result.set_err('{}'.format(result.value if result else result.error))

    def _check_mode(self, result):

        return result if self.mode == result.value else result.set_err('{}'.format(result.value if result else result.error))

    def is_idle(self):
        # return error if trex is not available

        return self._check_idle(self.server.check_status())

    def get_status(self):

        return self.server.check_status()

    def get_status_fast(self):
        # return error if trex is not available

        return self._check_idle(self.server.last_known_status())

    def get_mode_fast(self):
        # return error if trex is not available

        return self._check_mode(self.server.last_known_mode())

    def get_reservation(self):

        # trying to make reservation for current user
        result = self.server.take_reservation()

        # in case trex already reserved tries to cancel reservation
        if not result:
            result = self.server.cancel_reservation()

            # return error if cancel was not successful
            if not result:
                return result
            # trying to make reservation for current user after canceling
            result = self.server.take_reservation()

        return result

    def cancel_reservation(self):

        return self.server.cancel_reservation()

    def initialize(self):
        # makes checking and trying to make reservation

        # checking trex daemon status
        result = self.is_idle()
        # return error if trex is not available
        if not result:
            return result

        # in case alright returns status
        return self.get_reservation()

    def get_data(self, check_mode=None):

        # checking current trex client status
        result = Result()
        if not check_mode:
            status = True
        elif check_mode == CHECKMODE.fast:
            status = firstfilter(lambda x: not x, [self.get_status_fast(), self.get_mode_fast()], default=True)
        elif check_mode == CHECKMODE.full:
            status = self.is_idle()
        else:
            status = result.set_err('Unknown check mode <{}>'.format(check_mode))

        if not status:
            data = status
        else:

            logging.info('Test started with parameters: {}'.format(self.show_cfg()))

            data = self.client.run()

            logging.info('Test finished')

        return data

    def end(self, kill_force=False):

        # ending test

        result = Result()
        killed = Result()
        if self.server.check_reservation().value == TREXRESERV.reserved:
            cancel = self.cancel_reservation()
        else:
            cancel.set_val(TREXRESERV.free)

        # stop trex task
        if self.get_status().value == TREXSTATUS.running:
            killed = self.server.kill_soft()
        else:
            killed.set_val('killed')
        if not killed and kill_force:
            killed = self.server.kill_force()

        # which one contains error
        result = firstfilter(lambda x: not x, [killed, cancel], default=None)

        return killed if result is None else result

    def show_cfg(self):

        return {
            'server': {k: getattr(self.server.trex, k, None) for k in SERVER_DEFAULT},
            'test': self.client.get_cfg()}

    def run_loop(self, solver=solver, sargs=[], loop_count=100, check_mode=None, skwargs={}):

        mtd_params = {k: v for k, v in zip(['solver', 'sargs', 'skwargs', 'loop_count', 'check_mode'], [str(solver), sargs, skwargs, loop_count, check_mode])}
        logging.info('Test loop started with parameters: {}'.format(mtd_params))

        # initializes trex
        result = self.initialize()
        if not result:
            logging.error('Test loop ended. Init failed')
            return result

        # get 1st test data
        data = self.get_data(check_mode)
        # if error ocurred then exit

        if not data:
            logging.error('Test loop ended. No data')
            return data

        # data hub, contains results of tests
        # solver can change hub
        hub = [data.value]
        while loop_count > 0:
            # getting new params
            try:
                params = solver(hub, self.client.get_cfg(), *sargs, **skwargs)

            except SolverError as err:
                return result.set_err(err.message)
            # done
            if not params:
                break

            # test with new params
            self.client.set_cfg(params)
            data = self.get_data()

            # if error ocurred then exit
            if not data:
                return data

            hub.append(data.value)
            loop_count -= 1
        else:
            logging.info('Test loop exceeded. Loop was performed {} times. Test was ran {} times'.format(mtd_params['loop_count'], (mtd_params['loop_count'] + 1)))
            return result.set_err('Test loop count exceeded')

        # ending test
        end = self.end(kill_force=True)
        if not end:
            logging.warning('An error occured during finishing test: "{}"'.format(end.error))

        launched = (mtd_params['loop_count'] - loop_count)
        logging.info('Test loop ended. Loop was performed {} times. Test was ran {} times'.format(launched, (launched + 1)))

        # return data or error
        return result.set_val(hub) if result else result
