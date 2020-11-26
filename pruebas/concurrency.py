import signal
import asyncio
import functools

from typing import List, Callable, Dict, Tuple

try:
    import orjson as json
except ImportError:
    import json

DEBUG = False

# Code from: https://stackoverflow.com/a/37430948/8153205
def shutdown(stop_condition: asyncio.Event()):
    stop_condition.set()

def catch_signals(loop, fn):
    for sig_name in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig_name), fn)


class MemoryStreamQueue(asyncio.Queue):

    def __init__(self, max_cache: int = 1000, name: str = None):
        """
        Be careful with 'max_cache' value. It should be enough big for ensure
        that all consumers were finished before queue removes any element
        """
        super().__init__()
        self.__name = name or id(self)
        self.__max_cache = max_cache
        self.__offset = 0

    async def iterate(self, starts: int = 0):
        """starts value, by default, is the beginning of the queue"""

        current = 0

        while True:
            try:
                pos = abs(self.__offset - (current - starts))
                yield json.loads(self._queue[pos])

                current += 1
            except IndexError:
                getter = self._loop.create_future()
                self._getters.append(getter)
                try:
                    await getter
                except:
                    getter.cancel()  # Just in case getter is not done yet.
                    try:
                        # Clean self._getters from canceled getters.
                        self._getters.remove(getter)
                    except ValueError:
                        # The getter could be removed from self._getters by a
                        # previous put_nowait call.
                        pass
                    if not self.empty() and not getter.cancelled():
                        # We were woken up by put_nowait(), but can't take
                        # the call.  Wake up the next in line.
                        self._wakeup_next(self._getters)
                    raise

    def __repr__(self) -> str:
        return f"<MemoryStreamQueue - {self.__name} >"

    def _init(self, maxsize: int) -> None:
        self._queue = []

    def _get(self):
        return self._queue.pop(0)


    def _put(self, item):
        self._queue.append(json.dumps(item))

        # Purge queue
        if len(self._queue) > self.__max_cache:

            # Only purge
            if DEBUG:
                print("#"* 20, "purging!")
            print("Queue: ", len(self._queue))
            print("Getter: ", len(self._getters))
            print("Setter: ", len(self._putters))
            print("Unished tasks: ", self._unfinished_tasks)
            self._get()
            self.__offset += 1

            print("#" * 10, "after", "#" * 10)
            print("Queue: ", len(self._queue))
            print("Getter: ", len(self._getters))
            print("Setter: ", len(self._putters))
            print("Unished tasks: ", self._unfinished_tasks)


class _MainQueues:

    def __init__(self):
        self._queues = {}

    def __getattr__(self, item):
        try:
            return self._queues[item]
        except KeyError:
            m = MemoryStreamQueue(name=item)
            self._queues[item] = m
            return m

MainQueues = _MainQueues()

async def fn1(data: dict):
    print("fn 1: ", data)

    await MainQueues.ps2.put({"index": 1, "message": f"fn1 -> ps2"})
    await MainQueues.ps5.put(f"fn1 -> ps5")
    await asyncio.sleep(0.5)

async def fn2(data: dict):
    print("fn 2: ", data)

    await MainQueues.ps1.put(f"fn2 -> ps1")
    await MainQueues.ps8.put(f"fn2 -> ps8")
    await MainQueues.ps3.put(f"fn2 -> ps3")
    await asyncio.sleep(0.5)

async def fn3(data: dict):
    print("fn 3: ", data)

    await MainQueues.ps4.put(f"fn3 -> ps4")
    await MainQueues.ps5.put(f"fn3 -> ps5")
    await MainQueues.ps6.put(f"fn3 -> ps6")
    await asyncio.sleep(0.01)

async def worker(fn: Callable,
                 input_data: List[MemoryStreamQueue]):

    fn_name = fn.__name__

    async def queue_worker(fn: Callable,
                           fn_q: MemoryStreamQueue,
                           fn_lock: asyncio.Lock):

        try:
            if DEBUG:
                print("Running queue for fn: ", fn_name)
            index = 0  # First element
            async for data in fn_q.iterate():

                if DEBUG:
                    print(f"[{index}] Data queue for '{fn_name}' - {data}")

                async with fn_lock:
                    await fn(data)

                index += 1

        finally:
            print("Finishing queue worker for fn: ", fn.__name__)

    if DEBUG:
        print("Starting fn: ", fn_name)
    # This limit only one execution of function at time
    lock = asyncio.Lock()

    queue_workers = []
    for q in input_data:
        if DEBUG:
            print(f"fn: {fn_name} |", q)
        queue_workers.append(
            asyncio.create_task(queue_worker(fn, q, lock))
        )

    try:
        await asyncio.wait(queue_workers)
    finally:
        print("Finishing worker for function: ", fn.__name__)


async def run_workers(functions_map: Dict[Callable, List[MemoryStreamQueue]]):

    def force_stop_workers():
        for w in asyncio.all_tasks():
            w.cancel()

    loop = asyncio.get_event_loop()
    stop_condition = asyncio.Event()

    # Global stop condition
    catch_signals(loop, functools.partial(shutdown, stop_condition))

    workers = []
    workers_append = workers.append

    for fn, queues in functions_map.items():
        t = asyncio.create_task(worker(fn, input_data=queues))
        workers_append(t)

    # workers stop condition
    catch_signals(loop, force_stop_workers)

    await asyncio.wait(workers)


async def async_main():
    workers_map = {
        fn1: [MainQueues.ps1, MainQueues.ps3, MainQueues.ps4],
        fn2: [MainQueues.ps2, MainQueues.ps5, MainQueues.ps6],
        fn3: [MainQueues.ps1, MainQueues.ps3, MainQueues.ps8]
    }

    await MainQueues.ps1.put("p1 initial data")
    await MainQueues.ps2.put("p2 initial data")

    await run_workers(workers_map)

def main():

    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass

if __name__ == '__main__':
    main()
