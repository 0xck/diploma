import asyncio
import logging
from functools import wraps, partial
from concurrent.futures import ThreadPoolExecutor
from .tester import Tester
from .helper import TypeProperty, SEVERITY, Result
from .exceptions import TesterError, ExecutorError


class ExecutedTask():

    tester = TypeProperty('tester', Tester)
    pool = TypeProperty('pool', ThreadPoolExecutor)

    def __init__(self, tester, pool=None, loop=None):
        self.tester = tester
        self._int_run = False
        if loop:
            self._ext_loop = True
        else:
            loop = asyncio.get_event_loop()
            self._ext_loop = False
        self.loop = loop
        self.pool = pool or ThreadPoolExecutor(max_workers=2)
        self._task = None

    def _done_check(func):

        @wraps(func)
        def wrapper(self, *arsg, **kwargs):

            msg = 'Task is already done or canceled'
            template = partial('<{}> error occured during attempt <{func}> of <{cls}>'.format, func=func.__name__, cls=self.__class__.__name__)

            if self.loop.is_closed():
                logging.error(template(msg))

                raise ExecutorError(msg, lvl=SEVERITY.ERROR)

            return func(self, *arsg, **kwargs)

        return wrapper

    def stop(self):

        if self._task and not self._task.done():
            self.tester.end(kill_force=True)
            self._task.set_result(Result(error='Canceled'))

        if self._ext_loop or not self._int_run:
            return

        if self.loop.is_running():
            self.loop.stop()

        self.loop.close()

    @_done_check
    def get_task(self, **kwargs):

        tester_loop = partial(self.tester.run_loop, **kwargs)

        self._task = self.loop.run_in_executor(self._pool, tester_loop)

        return self._task

    @_done_check
    def run(self):

        try:
            logging.info('Task started')

            self._int_run = True

            return self.loop.run_until_complete(self.get_task())

        except TesterError as err:
            msg = 'Task failed'

            logging.error(msg)

            raise ExecutorError(msg, lvl=SEVERITY.ERROR) from err

        finally:
            self.stop()
