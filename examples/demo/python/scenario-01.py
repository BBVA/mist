import sys
import asyncio
from catalog import searchDomains, findOpenPorts

domain = sys.argv[1]

async def readQueueAndRun(q, f, *args):
    while True:
        asyncio.create_task(f(await q.get(), *args))

async def main():
    domainsQueue = asyncio.Queue()
    portsQueue = asyncio.Queue()
    asyncio.create_task(searchDomains(domain, domainsQueue))
    asyncio.create_task(readQueueAndRun(domainsQueue, findOpenPorts, "80,443", portsQueue))
    while True:
        print(await portsQueue.get())

asyncio.run(main())
