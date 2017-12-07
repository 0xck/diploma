"""
provides wrapper on trex client from trex API
"""
import logging
from functools import partial, wraps
from socket import gaierror as ResolvingError
from socket import timeout as TimeOut
from time import sleep
from collections import namedtuple
from .trex_client.stf.trex_stf_lib.trex_client import CTRexClient
from .trex_client.stf.trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexIncompleteRunError, TRexInUseError, TRexError, TRexException
from .trex_client.stl.trex_stl_lib.trex_stl_client import STLClient
from .trex_client.stl.trex_stl_lib.trex_stl_streams import STLProfile
from .trex_client.stl.trex_stl_lib.trex_stl_exceptions import STLError, STLTimeoutError
from .trex_client.external_libs.jsonrpclib.jsonrpc import ProtocolError
from .helper import TypeProperty, ValueProperty, Result, TREXMODE, TREXSTATUS, SEVERITY, FuncProperty, TREXRESERV
from .exceptions import TRexClientWrapperError, TRexSTLClientWrapperError


class TRexClientWrapper():
    """wrapper for client from CTRexClient trex API

    implements some of CTRexClient methods:
        creation trex client, ckecking trex status,
        taking and releasing reservation,
        killing tasks, running tests, returns test result
    """

    # trex attr (contains trex client obj) must be only CTRexClient
    trex = TypeProperty('trex', CTRexClient)
    # status tacken from actions and status checking
    # this is not real server status, useful for fast checking
    status = ValueProperty('status', (*TREXSTATUS, None))
    # trex mode started by client
    # useful for fast checking
    mode = ValueProperty('mode', (*TREXMODE, None))
    sampler = FuncProperty('sampler', lambda x: x > 0)

    @staticmethod
    def _get_client(config):
        """returns trex client obj of CTRexClient from trex API

        returns (CTRexClient): trex client API obj which is created with given settings
        raises (TRexClientWrapperError): exception in case fail
        """

        # trying to create trex client
        try:
            return CTRexClient(**config)

        except ResolvingError:
            logging.warning('Can not resolve TRex server name {}'.format(config.get('trex_host', 'unknown')))
            TRexClientWrapperError('Resolving error', lvl=SEVERITY.WARNING)

    def __init__(self, server, test, sampler):
        """creating trex client

        args:
            server (dict): has to contain trex server settings
            test (dict): has to contain trex test settings
        """
        # gettig client
        self.trex = self._get_client(server)
        self.test = test
        # status taken from actions and status checking
        self.status = None
        # trex mode started by client
        self.mode = None
        self.sampler = int(sampler)

    def _trex_exception_handler(func):
        """decorator for handling common trex server error

        catches certain exceptons returns formated error
        makes log entry for critical and connection related issues

        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            result = Result()
            # error template
            template = partial('<{}> error occured during attempt <{func}> of <{cls}>'.format, func=func.__name__, cls=self.__class__.__name__)

            try:
                return func(self, *args, **kwargs)

            # connection error
            except (ConnectionRefusedError, TimeOut):
                logging.warning(template('TRex {} is unavailable'.format(self.trex.trex_host)))
                result.set_err(template('TRex is unavailable'))

            except ResolvingError:
                logging.warning(template('Can not resolve TRex server name {}'.format(self.trex.trex_host)))
                result.set_err(template('Resolving error'))

            # ordinary trex errors
            # other user already reserved trex
            except TRexRequestDenied as err:
                result.set_err(template('Request Denied'))
            # trex is alredy in use
            except TRexInUseError:
                result.set_err(template('TRex server already has running test'))

            # critical errors
            # TRex process itself terminated with error fault or it has been terminated by an external intervention in the OS
            except TRexIncompleteRunError as err:
                logging.critical('{} for {}. "{}"'.format(template('TRex server fault'), self.trex.trex_host, err.msg))
                result.set_err(template('TRex server fault'))
            # General trex issue, something is wrong with API code; very serios
            except TRexException as err:
                # TRexException is common exception for subexceptions
                # code checks if one is TRexException else subexceptions
                # checking it is TRexException itself not its heir
                if err.__class__ not in TRexException.__mro__:
                    logging.critical('{} for {}. "{}"'.format(template('TRex API'), self.trex.trex_host, err.msg))
                    result.set_err(template('TRex API'))
                else:
                    logging.error('{} "{}"'.format(template('Unknown TRex ' + err.__class__.__name__), err.msg))
                    raise err
            # JSON-RPC erros, something is wrong with code or server
            except ProtocolError:
                logging.error('{} for {}'.format(template('TRex RPC'), self.trex.trex_host))
                result.set_err(template('TRex RPC'))

            return result
        return wrapper

    def last_known_status(self):

        result = Result()
        return result.set_val(self.status)

    def last_known_mode(self):

        result = Result()
        return result.set_val(self.mode)

    def set_cfg(self, config):
        self.test = config

    def get_cfg(self):
        return self.test

    @_trex_exception_handler
    def kill_force(self):
        # force kills all trex tasks

        result = Result()
        return result.set_val('killed') if self.trex.force_kill(confirm=False) else result.set_err('Unsuccessfull force kill')

    @_trex_exception_handler
    def kill_soft(self):
        # soft kills all trex tasks

        result = Result()
        return result.set_val('killed') if self.trex.stop_trex() else result.set_err('Unsucessfull force kill')

    @_trex_exception_handler
    def check_idle(self):

        result = Result()
        if self.trex.is_idle():
            # has active test
            result.set_val(TREXSTATUS.running)
            self.status = TREXSTATUS.running
        else:
            result.set_err(TREXSTATUS.running)
            self.status = TREXSTATUS.idle

        return result

    @_trex_exception_handler
    def check_status(self):
        """returns information about trex server status and availability

        trex daemon status info
        checking if trex demon is running
        checking general connectivity
        """

        result = Result()
        # checking daemon connectivity
        if not self.trex.check_server_connectivity():
            result.set_val(TREXSTATUS.unavailable)
            self.status = TREXSTATUS.unavailable
        # cheking is trex is running (not idle)
        elif self.check_idle():
            # has active test
            result.set_val(TREXSTATUS.idle)
        else:
            result.set_val(TREXSTATUS.running)

        return result

    @_trex_exception_handler
    def take_reservation(self):
        # takes reservation

        result = Result()
        return result.set_val(TREXRESERV.reserved) if self.trex.reserve_trex(user=None) else result.set_err('Can not take reservation')

    @_trex_exception_handler
    def check_reservation(self):
        # checks if trex is reserved

        result = Result()
        return result.set_val(TREXRESERV.reserved) if self.trex.is_reserved() else result.set_val(TREXRESERV.free)

    @_trex_exception_handler
    def cancel_reservation(self):
        # cancels reservation

        result = Result()
        return result.set_val(TREXRESERV.free) if self.trex.cancel_reservation(user=None) else result.set_err('Can not cancel reservation')

    @_trex_exception_handler
    def start_stl(self, **trex_cmd_options):
        """starts stl mode
        """

        result = Result()
        try:
            if self.trex.start_stateless(**trex_cmd_options):
                result.set_val('TRex stl started')
                self.status = TREXSTATUS.running
                self.mode = TREXMODE.stl
            else:
                result.set_err('TRex stl starting failed')

        # the wrong trex server option raised the exception
        except TRexError as err:
            result.set_err(err.msg)

        return result

    @_trex_exception_handler
    def start_stf(self):
        """starts stf test
        """

        result = Result()
        try:
            if self.trex.start_trex(**self.test):
                result.set_val('TRex stf started')
                self.status = TREXSTATUS.running
                self.mode = TREXMODE.stf
            else:
                result.set_err('TRex stf starting failed')

        # some params may be wrong
        except (TypeError, ValueError) as err:
            result.set_err(err.args)
        # the wrong trex server option raised the exception
        except TRexError as err:
            result.set_err(err.msg)

        return result

    @_trex_exception_handler
    def _get_data(self):
        """returns stf test result with given sampling as CTRexResult obj

        kwargs:
            sampler (int): determines the time (in seconds) between each sample of the server, default is 1

        return (Result):
            success:
                result.value (TRexResult): TRexResult obj with sampled result (raw data)
            fail:
                result.error (str): error string
        """

        result = Result()
        try:
            # getting data from trex server
            result.set_val(self.trex.sample_until_finish(time_between_samples=self.sampler))

        # something went wrong and trex client can not processed returned from server json
        except TypeError:
            logging.error('JSON stream decoding error during getting data on {}'.format(self.trex.trex_host))
            result.set_err('JSON stream decoding error', lvl=SEVERITY.ERROR)

        self.status = TREXSTATUS.idle
        self.mode = None

        # returns data/error in case success/no success
        return result

    def run(self):
        started = self.start_stf()
        if not started:
            return started

        return self._get_data()


class TRexSTLClientWrapper():

    trex = TypeProperty('trex', TRexClientWrapper)
    client = TypeProperty('client', STLClient)
    sampler = FuncProperty('sampler', lambda x: x > 0)

    @staticmethod
    def _get_client(config):
        """returns trex client obj of CTRexClient from trex API

        returns (CTRexClient): trex client API obj which is created with given settings
        raises (TRexClientWrapperError): exception in case fail
        """

        # trying to create trex client
        try:
            return STLClient(**config)

        except STLError as err:
            raise TRexSTLClientWrapperError(err.msg)

    @staticmethod
    def as_ntuple(config):
        # returns namedtuple from dict

        sconfig = sorted(config)
        try:
            ntuple = namedtuple('ntuple', sconfig)
            return ntuple(*(config[i] for i in sconfig))
        except ValueError as err:
            raise TRexSTLClientWrapperError('Wrong value in given settings', content=[type(err), err.args])

    def __init__(self, trex, client, test, sampler):
        """creating stl client

        arsg:
            trex (TRexClientWrapper): mng for trex server
            test (dict): has to contain stl test settings
        """

        # default trex server config
        self.trex = trex
        self.test_raw = test
        cfg = self.as_ntuple(self.test_raw)
        if not len(cfg):
            raise TRexSTLClientWrapperError('Empty config', content=self.test_raw)
        self.test = cfg
        # getting client
        self.client = self._get_client(client)
        self.sampler = int(sampler)

    def _stl_exception_handler(func):
        """decorator for handling common trex server error

        catches certain exceptons returns formated error
        makes log entry for critical and connection related issues

        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            result = Result()
            # error template
            templ_log = partial('<{}> error occured during attempt <{func}> of <{cls}>'.format, func=func.__name__, cls=self.__class__.__name__)
            template = partial('An error occured during attempt <{func}> of <{cls}>. "{}"'.format, func=func.__name__, cls=self.__class__.__name__)

            try:
                return func(self, *args, **kwargs)

            # connection error
            except (ConnectionRefusedError, TimeOut, STLTimeoutError):
                logging.warning(templ_log('TRex {} is unavailable'.format(self.trex)))
                result.set_err('TRex is unavailable')

            except ResolvingError:
                logging.warning(templ_log('Can not resolve TRex server name {}'.format(self.trex)))
                result.set_err('Resolving error')

            # ordinary trex errors
            # other user already reserved trex
            except STLError as err:
                result.set_err(template(err.msg))

            except AttributeError as err:
                raise TRexSTLClientWrapperError('Wrong or not implemented attribute', content=err.args)

            return result
        return wrapper

    def set_cfg(self, config):

        self.test_raw = config
        cfg = self.as_ntuple(config)
        if not len(cfg):
            raise TRexSTLClientWrapperError('Empty config', content=config)
        self.test = cfg

    def get_cfg(self):

        return self.test_raw

    @_stl_exception_handler
    def _get_streams(self):
        # getting streams from local file

        result = Result()
        return result.set_val(STLProfile.load(self.test.pattern, port_id=self.test.act_iface))

    @_stl_exception_handler
    def _connect(self):

        result = Result()
        self.client.connect()
        return result.set_val('Connected')

    @_stl_exception_handler
    def _disconnect(self):
        # diconnect with stoping traffic and releasing ports

        result = Result()
        self.client.disconnect()
        return result.set_val('Disconnected')

    @_stl_exception_handler
    def _acquire(self):
        # acquires given ports

        result = Result()
        return result.set_val('Acquired {}'.format(self.client.acquire(ports=self.test.ifaces)))

    @_stl_exception_handler
    def _release(self):
        # acquires given ports

        result = Result()
        return result.set_val('Released {}'.format(self.client.release(ports=self.test.ifaces)))

    @_stl_exception_handler
    def _reset(self):
        # Force acquire ports, stop the traffic, remove all streams and clear stats

        result = Result()
        self.client.reset(ports=self.test.ifaces)
        return result.set_val('Ports were reseted')

    @_stl_exception_handler
    def _set_service_mode(self):

        result = Result()
        self.client.set_service_mode(ports=self.test.act_iface, enabled=True)
        return result.set_val('Port {} is in service mode'.format(self.test.act_iface))

    @_stl_exception_handler
    def _cancel_service_mode(self):

        result = Result()
        self.client.set_service_mode(ports=self.test.act_iface, enabled=False)
        return result.set_val('Port {} is out of service mode'.format(self.test.act_iface))

    @_stl_exception_handler
    def _arp_resolve(self):
        # makes ARP resolution in service mode

        result = Result()
        self._set_service_mode()
        self.client.arp(ports=self.test.act_iface, retries=self.test.arp_retries)
        self._cancel_service_mode()

        return result.set_val('ARP resolved')

    @_stl_exception_handler
    def _add_streams(self):

        result = Result()

        streams = self._get_streams()
        if not streams:
            return streams

        streams = self.client.add_streams(streams.value, ports=self.test.act_iface)
        return result.set_val('Streams {} were added'.format(streams))

    @_stl_exception_handler
    def _start(self):
        # starts test

        result = Result()
        self.client.start(
            ports=self.test.act_iface,
            mult='{}{}'.format(self.test.rate, self.test.rate_type),
            duration=(self.test.duration + self.test.warm))

        return result.set_val('Started')

    @_stl_exception_handler
    def _stop(self):

        result = Result()
        self.client.stop()
        return result.set_val('Stopped')

    def _finish(self, kill_force=False):

        self._disconnect()
        # stop trex task
        killed = self.trex.kill_soft()
        if not killed and kill_force:
            killed = self.trex.kill_force()

        return killed

    @_stl_exception_handler
    def _get_data(self):

        result = Result()
        # pseudo sampler for getting stats
        pseudo_sampler = []
        count = 0
        wait_for = round(self.test.duration / self.sampler)
        # getting stats for pseudo sampler exclude first and last
        # waiting for warming end
        sleep(self.test.warm)
        # getting data
        while count < wait_for:
            data = self.client.get_stats(ports=self.test.ifaces, sync_now=True)
            # for compatibility with stateful
            data['queue_drop'] = 0
            pseudo_sampler.append(data)
            count += 1
            sleep(self.sampler)

        # waiting for end and getting final data
        self.client.wait_on_traffic(ports=self.test.ifaces)
        pseudo_sampler.append(self.client.get_stats(ports=self.test.ifaces, sync_now=True))

        return result.set_val(pseudo_sampler)

    def run(self, kill_force=False):

        start_seq = [
            self.trex.start_stl,
            self._connect,
            self._reset,
            self._arp_resolve,
            self._add_streams,
            self._start]

        for mtd in start_seq:
            result = mtd()
            if not result:
                self._finish()
                return result

        # getting data
        data = self._get_data()

        # disconnecting
        self._finish()

        # returns error or data
        return data
