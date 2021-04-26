import sys, asyncio, inspect
from catalog import searchDomains, findOpenPorts

done = 0

async def producer(f, *args):
    await asyncio.create_task(f(*args))
    global done
    done = done + 1 

async def consumer(q, f, n, *args):
    global done
    while not q.empty() or done < n:
        try:
            item = q.get_nowait()
            if inspect.iscoroutinefunction(f):
                await f(item, *args)
            else:
                f(item, *args)
        except asyncio.QueueEmpty as e:
            await asyncio.sleep(2)
    done = done + 1

async def main():
    tasks = []
    domainsQueue = asyncio.Queue()
    portsQueue = asyncio.Queue()
    tasks.append(asyncio.create_task(producer(searchDomains, sys.argv[1], domainsQueue)))
    tasks.append(asyncio.create_task(consumer(domainsQueue, findOpenPorts, 1, "80,443", portsQueue)))
    tasks.append(asyncio.create_task(consumer(portsQueue, print, 2)))
    await asyncio.gather(*tasks)

asyncio.run(main())
