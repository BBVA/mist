import sys, asyncio
from catalog import searchDomains, findOpenPorts
from aux import consumer, producer

async def main():
    tasks = []
    foundDomains = asyncio.Queue()
    portsQueue = asyncio.Queue()
    tasks.append(asyncio.create_task(producer(searchDomains, sys.argv[1], foundDomains)))
    tasks.append(asyncio.create_task(consumer(foundDomains, findOpenPorts, 1, "80,443", portsQueue)))
    tasks.append(asyncio.create_task(consumer(portsQueue, print, 2)))
    await asyncio.gather(*tasks)

asyncio.run(main())
