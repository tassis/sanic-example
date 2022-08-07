import asyncio
import inspect
import traceback
from sanic.log import logger
from datetime import timedelta, time, datetime
from sanic import Sanic
from typing import Callable, Mapping, Optional, Union

class AppScheduleTask:
    
    def __init__(self, name: str,
                       callback: Callable, 
                       period: Optional[timedelta],
                       start_time:Optional[Union[timedelta, time]],
                       utc: bool):
        self.name = name
        self.callback = callback
        self.period = period
        self.start_time = start_time
        self.utc = utc
        self.__next_start_time = None
        self.__run_task = None

    def _get_next_delta(self):
        # Get current time.
        now = datetime.utcnow().replace(microsecond=0)
        if not self.utc:
            now = datetime.now().replace(microsecond=0)

        # if have start_time, calculate next start time offset.
        if self.start_time is not None:
            if isinstance(self.start, time):
                d1 = datetime.combine(datetime.min, self.start_time)
                d2 = datetime.combine(datetime.min, now.time())
                start_offset = timedelta(seconds=(d1 - d2).seconds)

            self.__next_start_time = now + start_offset
        else:
            self.__next_start_time = now

        if not self.period:
            return 

        while self.__next_start_time <= now:
            self.__next_start_time += self.period

        return int((self.__next_start_time - now).total_seconds())

    async def run(self, app: Sanic):
        while True:
            delta = self._get_next_delta()
            # if the time is not up, wait for it.
            if delta:
                await asyncio.sleep(delta)

            logger.debug(f"RUN TASK - {self.name}")
            try:
                ret = self.callback()
                if inspect.isawaitable(ret):
                    await ret

                logger.debug(f"END TASK - {self.name}")
                # execute task
                if delta is None:
                    break

                # logger.info(f"TASK {self.name} END")
            except Exception as _e:
                logger.error(_e)
                logger.error(traceback.format_exc())

    async def start(self, app: Sanic):
        self.__run_task = app.add_task(self.run(app))

    async def stop(self):
        if self.__run_task:
            self.__run_task.cancel()


class AppScheduler:
    
    def __init__(self, app: Sanic=None):
        self.app = app
        self._registerd_task: Mapping[str, AppScheduleTask] = {}

    def task_list(self):
        return self._registerd_task.items()

    def get_task(self, name: str):
        return self._registerd_task.get(name)

    def register_task_handler(self, name: str, 
                                    func: Callable,
                                    period: Optional[timedelta] = None,
                                    start_time: Optional[time] = None,
                                    utc: Optional[bool]=True):
        self._registerd_task[name] = AppScheduleTask(name, func, period, start_time, utc)
    
    def register_task(self, name: str, 
                            period: Optional[timedelta] = None, 
                            start_time: Optional[time] = None,
                            utc: Optional[bool] = None):
        def wrapper(callback):
            self.register_task_handler(name, callback, period, start_time, utc)
            return callback
        return wrapper

    async def run_scheduler(self, app: Sanic):
        for task in self._registerd_task.values():
            await task.start(app)
    
    async def stop_scheduler(self):
        for task in self._registerd_task.values():
            await task.stop()
