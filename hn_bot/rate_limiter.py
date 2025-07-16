import asyncio
import queue
from dataclasses import dataclass


# Rate limiter class for rate limiting async tasks
# Strictly limits the number of calls
#
# The current implementation is primitive and does not account for early/late wakeups
@dataclass(init=False)
class RateLimiter:
    waiting: queue.Queue[asyncio.Future[None]]
    # number of requests per interval
    requests_per_interval: int

    # length of the time interval in seconds
    interval: float

    # length between calls
    time_between_calls: float

    # last timestamp
    last_call: float

    def __init__(self, requests_per_interval: int, interval: float):
        self.waiting = queue.Queue()
        self.requests_per_interval = requests_per_interval
        self.interval = interval
        self.time_between_calls = interval / requests_per_interval
        self.last_call = 0

    def __current_time(self):
        loop = asyncio.get_running_loop()
        return loop.time()

    def __next_time(self):
        return self.last_call + self.time_between_calls

    # get the next time as a float in seconds, so we can schedule the call in the event loop
    def __remaining_wait_time(self):
        wait_time = self.time_between_calls - (self.__current_time() - self.last_call)

        if wait_time < 0:
            return 0
        else:
            return wait_time

    def __wake_one(self):
        if self.__current_time() < self.__next_time():
            print("woke up too early")

        if self.waiting.empty():
            return
        else:
            future = self.waiting.get()
            future.set_result(None)
            self.last_call = self.__current_time()

        if not self.waiting.empty():
            loop = asyncio.get_running_loop()
            _ = loop.call_later(self.__remaining_wait_time(), self.__wake_one)

    async def wait(self):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        if self.waiting.empty():
            current_time = self.__current_time()

            # if no requests have happenend in a while we can immediately make this one
            if current_time >= self.__next_time():
                self.last_call = current_time
                return
            else:
                self.waiting.put(future)
                _ = loop.call_later(
                    self.__remaining_wait_time(),
                    self.__wake_one,
                )
        else:
            self.waiting.put(future)

        await future
