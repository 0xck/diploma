"""
provides wrapper on trex client from trex API
"""
import logging
from functools import partial, wraps
from socket import gaierror as ResolvingError
from socket import timeout as TimeOut
from time import sleep
from trex_stf_lib.trex_client import CTRexClient
from trex_stf_lib.trex_exceptions import TRexRequestDenied, TRexIncompleteRunError, TRexInUseError, TRexError, TRexException
from trex_stl_lib.trex_stl_client import STLClient
from trex_stl_lib.trex_stl_streams import STLProfile
from trex_stl_lib.trex_stl_exceptions import STLError, STLTimeoutError
from external.libs.jsonrpclib import ProtocolError
from helper import TypeProperty, ValueProperty, Result, TREXMODE, TREXSTATUS, SEVERITY
from exceptons import TRexClientWrapperError, ProcessorError, TRexSTLClientWrapperError
from processors.stf import processor as stf_processor
from processors.stl import processor as stl_processor


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
    status = ValueProperty('status', [*TREXSTATUS, None])
    # trex mode started by client
    # useful for fast checking
    mode = ValueProperty('mode', [*TREXMODE, None])

    @staticmethod
    def _get_client(**kwargs):
        """returns trex client obj of CTRexClient from trex API

        returns (CTRexClient): trex client API obj which is created with given settings
        raises (TRexClientWrapperError): exception in case fail
        """

        # trying to create trex client
        try:
            return CTRexClient(**kwargs)

        except ResolvingError:
            logging.warning('Can not resolve TRex server name {}'.format(kwargs.get('trex', 'unknown')))
            TRexClientWrapperError('Resolving error', lvl=SEVERITY.WARNING)

    def __init__(self, **kwargs):
        """creating trex client

        kwargs: has to contain trex server settings
        """
        # gettig client
        self.trex = self._get_client(**kwargs)
        # status taken from actions and status checking
        self.status = None
        # trex mode started by client
        self.mode = None

    def trex_exception_handler(func):
        """decorator for handling common trex server error

        catches certain exceptons returns formated error
        makes log entry for critical and connection related issues

        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            result = Result()
            # error template
            template = partial('{} error occured during attempt {reason}'.format, reason=func.__name__)

            try:
                return func(self, *args, **kwargs)

            # connection error
            except (ConnectionRefusedError, TimeOut):
                logging.warning('TRex {} is unavailable'.format(self.trex.trex_host))
                result.set_err(template('TRex is unavailable'))

            except ResolvingError:
                logging.warning('Can not resolve TRex server name {}'.format(self.trex.trex_host))
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
                logging.critical('{} for {}'.format(template('TRex RPC'), self.trex.trex_host))
                result.set_err(template('TRex RPC'))

            return result
        return wrapper

    def last_known_status(self):
        return self.status

    def last_known_mode(self):
        return self.mode

    @trex_exception_handler
    def kill_force(self):
        # force kills all trex tasks

        result = Result()
        return result.set_val('killed') if self.trex.force_kill(confirm=False) else result.set_err('Unsuccessfull force kill')

    @trex_exception_handler
    def kill_soft(self):
        # soft kills all trex tasks

        result = Result()
        return result.set_val('killed') if self.trex.stop_trex() else result.set_err('Unsucessfull force kill')

    @trex_exception_handler
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

        # cheking is trex has active test
        elif self.trex.is_running():
            # has active test
            result.set_val(TREXSTATUS.running)
            self.status = TREXSTATUS.running
        else:
            result.set_val(TREXSTATUS.idle)
            self.status = TREXSTATUS.idle

        return result

    @trex_exception_handler
    def take_reservation(self):
        # takes reservation

        result = Result()
        return result.set_val('Reserved') if self.trex.reserve_trex(user=None) else result.set_err('Can not take reservation')

    @trex_exception_handler
    def check_reservation(self):
        # checks if trex is reserved

        result = Result()
        return result.set_val('reserved') if self.trex.is_reserved() else result.set_val('free')

    @trex_exception_handler
    def cancel_reservation(self):
        # cancels reservation

        result = Result()
        return result.set_val('Reservation canceled') if self.trex.cancel_reservation(user=None) else result.set_err('Can not cancel reservation')

    @trex_exception_handler
    def start_stf(self, **kwargs):
        """starts stf test

        kwargs: has to contain test settings
        """

        result = Result()
        try:
            if self.trex.start_trex(**kwargs):
                result.set_val('TRex stf started')
                self.status = TREXSTATUS.running
                self.mode = TREXMODE.stf
            else:
                result.set_err('TRex stf starting failed')

        # "d" parameter inserted with wrong value one must be at least 30 seconds long
        except ValueError:
            result.set_err('duration is wrong')
        # the wrong trex server option raised the exception
        except TRexError as err:
            result.set_err(err.msg)

        return result

    @trex_exception_handler
    def start_stl(self, **kwargs):
        """starts stl mode

        kwargs: has to contain test settings
        """

        result = Result()
        try:
            if self.trex.start_stateless(**kwargs):
                result.set_val('TRex stl started')
                self.status = TREXSTATUS.running
                self.mode = TREXMODE.stl
            else:
                result.set_err('TRex stl starting failed')

        # the wrong trex server option raised the exception
        except TRexError as err:
            result.set_err(err.msg)

        return result

    @trex_exception_handler
    def gather_stf(self, sampler=1, processor=stf_processor, pargs=[], pkwargs={}, **kwargs):
        """returns stf test result with given sampling as CTRexResult obj

        raw data may be processed with given processor function
        ! method does not intercept processor exceptions, besides trex exceptions
        ! method knows nothing about data type, this is task of processor

        kwargs:
            sampler (int): determines the time (in seconds) between each sample of the server, default is 1
            processor (function): traffic handler function,
                if not None then raw data will be procesed with processor,
                default is stf_processor
            pargs (list): processor args list, default is empty
            pkwargs (dict): processor args dict, default is empty

        return (Result):
            success:
                result.value (`seq`) if processor was defined
                result.value (TRexResult): TRexResult obj with sampled result (raw data) if prosessor is None
            fail:
                result.error (str): error string
        """

        result = Result()
        try:
            # getting data from trex server
            data = self.trex.sample_until_finish(time_between_samples=sampler)

        # something went wrong and trex client can not processed returned from server json
        except TypeError:
            return result.set_err('JSON stream decoding error')
        # something went wrong during processing data
        except ProcessorError as err:
            logging.error(err.message)
            return result.set_err(err.message)

        # processes data with external processor if one is defined
        processed = (processor(data, *pargs, **pkwargs)) if processor else data
        self.status = TREXSTATUS.idle
        self.mode = None

        # returns data/error in case success/no success
        return result.set_val(processed) if processed else result.set_err('No data')

    def _get_stl_client(self, **kwargs):

        result = Result()
        try:
            result.add_val(TRexSTLClientWrapper(self.trex.trex_host, **kwargs))
        except TRexSTLClientWrapperError as err:
            result.set_err(err.message)

        return result

    def gather_stl(self, processor=stl_processor, pargs=[], pkwargs={}, **kwargs):

        client = self._get_stl_client(**kwargs)

        if not client:
            return client

        result = Result()
        # waiting for getting data
        data = client.run()
        # processes data with external processor if one is defined
        processed = (processor(data, *pargs, **pkwargs)) if processor else data

        self.status = TREXSTATUS.idle
        self.mode = None

        # returns data/error in case success/no success
        return result.set_val(processed) if processed else result.set_err('No data')

    def run_stf(self, **kwargs):
        started = self.start_stf(**kwargs)
        if not started:
            return started

        return self.gather_stf(**kwargs)

    def run_stl(self, **kwargs):
        started = self.start_stl(**kwargs)
        if not started:
            return started

        return self.gather_stl(**kwargs)


class TRexSTLClientWrapper():

    client = TypeProperty('client', STLClient)

    @staticmethod
    def _get_client(**kwargs):
        """returns trex client obj of CTRexClient from trex API

        returns (CTRexClient): trex client API obj which is created with given settings
        raises (TRexClientWrapperError): exception in case fail
        """

        # trying to create trex client
        try:
            return STLClient(**kwargs)

        except (ConnectionRefusedError, TimeOut, STLTimeoutError):
            logging.warning('TRex {} is unavailable'.format(kwargs.get('server', 'unknown')))
            raise TRexSTLClientWrapperError('TRex is unavailable', lvl=SEVERITY.WARNING)

        except ResolvingError:
            logging.warning('Can not resolve TRex server name {}'.format(kwargs.get('server', 'unknown')))
            TRexSTLClientWrapperError('Resolving error', lvl=SEVERITY.WARNING)

        except STLError as err:
            raise TRexSTLClientWrapperError(err.msg)

    def __init__(self, trex, stl_config=None, **kwargs):
        """creating stl client

        arsg:
            trex (str): mng for trex server

        kwargs:
            stl_config (): has to contain stl test settings
            kwargs: additional trex settings
        """

        # default trex server config
        self.trex = trex

        if not stl_config:
            raise TRexSTLClientWrapperError('Empty config for stl')
        self.config = stl_config

        # change trex host for ruled by current trex client
        kwargs.update({'server': self.trex})
        # getting client
        self.client = self._get_client(**kwargs)

    def stl_exception_handler(func):
        """decorator for handling common trex server error

        catches certain exceptons returns formated error
        makes log entry for critical and connection related issues

        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            result = Result()
            # error template
            template = partial('An error occured during attempt {reason}. "{}"'.format, reason=func.__name__)

            try:
                return func(self, *args, **kwargs)

            # connection error
            except (ConnectionRefusedError, TimeOut, STLTimeoutError):
                logging.warning('TRex {} is unavailable'.format(self.trex))
                result.set_err('TRex is unavailable')

            except ResolvingError:
                logging.warning('Can not resolve TRex server name {}'.format(self.trex))
                result.set_err('Resolving error')

            # ordinary trex errors
            # other user already reserved trex
            except STLError as err:
                result.set_err(template(err.msg))

            return result
        return wrapper

    @stl_exception_handler
    def _get_streams(self):
        # getting streams from local file

        result = Result()
        return result.set_val(STLProfile.load(self.config.pattern))

    @stl_exception_handler
    def _connect(self):

        result = Result()
        self.client.connect()
        return result.set_val('Connected')

    @stl_exception_handler
    def _disconnect(self):
        # diconnect with stoping traffic and releasing ports

        result = Result()
        self.client.disconnect()
        return result.set_val('Disconnected')

    @stl_exception_handler
    def _acquire(self):
        # acquires given ports

        result = Result()
        self.client.acquire(ports=self.config.ifaces)
        return result.set_val('Acquired')

    @stl_exception_handler
    def _reset(self):
        # Force acquire ports, stop the traffic, remove all streams and clear stats

        result = Result()
        self.client.reset(ports=self.config.ifaces)
        return result.set_val('Statistic was reseted')

    @stl_exception_handler
    def _set_service_mode(self):

        result = Result()
        self.client.set_service_mode(ports=self.config.act_iface, enabled=True)
        return result.set_val('Port {} is in service mode'.format(self.config.act_iface))

    @stl_exception_handler
    def _cancel_service_mode(self):

        result = Result()
        self.client.set_service_mode(ports=self.config.act_iface, enabled=False)
        return result.set_val('Port {} is out of service mode'.format(self.config.act_iface))

    @stl_exception_handler
    def _arp_resolve(self):
        # makes ARP resolution in service mode

        result = Result()
        self._set_service_mode()
        self.client.arp(ports=self.config.act_iface, retries=self.config.arp_retries)
        self._cancel_service_mode()

        return result.set_val('ARP resolved')

    @stl_exception_handler
    def _add_streams(self):

        result = Result()
        self.client.add_streams(ports=self.config.act_iface)
        return result.set_val('Streams were added')

    @stl_exception_handler
    def _start(self):
        # starts test

        result = Result()
        self.client.start(
            ports=self.config.act_iface,
            mult='{}{}'.format(self.config.rate, self.config.rate_type),
            duration=(self.config.duration + self.config.warm))

        return result.set_val('Started')

    @stl_exception_handler
    def _get_data(self):

        result = Result()
        # pseudo sampler for getting stats
        pseudo_sampler = []
        count = 0
        wait_for = round(self.config.duration / self.config.sampler)
        # getting stats for pseudo sampler exclude first and last
        # waiting for warming end
        sleep(self.config.warm)
        # getting data
        while count < wait_for:
            data = self.client.get_stats(ports=self.config.ifaces, sync_now=True)
            # for compatibility with stateful
            data['queue_drop'] = 0
            pseudo_sampler.append(data)
            count += 1
            sleep(self.config.sampler)

        # waiting for end and getting final data
        self.client.wait_on_traffic(ports=self.config.ifaces)
        pseudo_sampler.append(self.client.get_stats(ports=self.config.ifaces, sync_now=True))

        return result.add_val(pseudo_sampler)

    def run(self):

        for mtd in [self._connect, self._reset, self._arp, self._add_streams, self._start]:
            result = mtd()
            if not result:
                return result

        # getting data
        data = self._get_data()

        # disconnecting
        finish = self._disconnect()

        return data if finish else finish
