import asyncio
import json

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
        currentTask = asyncio.current_task()

        while True:
            try:
                currentTask.waitingForQueue = False
                pos = abs(self.__offset - (current - starts))
                yield json.loads(self._queue[pos])
                current += 1
            except IndexError:
                getter = self._loop.create_future()
                self._getters.append(getter)
                try:
                    currentTask.waitingForQueue = True
                    await asyncio.wait_for(getter, 2)
                except asyncio.exceptions.TimeoutError:
                    if current == self.qsize() and all(t.done() for t in producers if t != currentTask and not t.waitingForQueue):
                        return
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
            # print("Queue: ", len(self._queue))
            # print("Getter: ", len(self._getters))
            # print("Setter: ", len(self._putters))
            # print("Unished tasks: ", self._unfinished_tasks)
            self._get()
            self.__offset += 1

            # print("#" * 10, "after", "#" * 10)
            # print("Queue: ", len(self._queue))
            # print("Getter: ", len(self._getters))
            # print("Setter: ", len(self._putters))
            # print("Unished tasks: ", self._unfinished_tasks)

class _Streams(dict):

    def __init__(self):
        super(_Streams, self).__init__()

    def createIfNotExists(self, name):
        if not name in self:
            self[name] = MemoryStreamQueue(name=name)

    async def send(self, name, value):
        self.createIfNotExists(name)
        await self[name].put(value)

streams = _Streams()
consumers = []
producers = []

__all__ = ("streams", "consumers", "producers",)
