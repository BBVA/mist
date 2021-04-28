import sys, asyncio, os
from catalog import searchDomains, findOpenPorts, kafkaProducer, festin, filterRepeated, S3Store, S3Write
from aux import consumer, producer

async def dispatcher(p, kafkaQ, S3Q):
    if p["port"] == "80":
        await kafkaQ.put(p)
    else:
        await S3Q.put(p)

async def main():
    tasks = []
    
    foundDomains = asyncio.Queue()
    filteredDomains = asyncio.Queue()
    portsQueue = asyncio.Queue()
    kafkaQueue = asyncio.Queue()
    S3Queue = asyncio.Queue()

    tasks.append(asyncio.create_task(producer(searchDomains, sys.argv[1], foundDomains)))
    tasks.append(asyncio.create_task(producer(festin, sys.argv[1], os.environ["DNS_SERVER"], True, foundDomains)))

    tasks.append(asyncio.create_task(consumer(foundDomains, findOpenPorts, 2, "80,443", filteredDomains)))
    tasks.append(asyncio.create_task(consumer(filteredDomains, filterRepeated, 3, portsQueue)))
    tasks.append(asyncio.create_task(consumer(portsQueue, dispatcher, 4, kafkaQueue, S3Queue)))

    tasks.append(asyncio.create_task(consumer(kafkaQueue, kafkaProducer, 5, os.environ["KAFKA_SERVER"], "domainsTopic")))
    tasks.append(asyncio.create_task(consumer(S3Queue, S3Store, 6)))
    
    await asyncio.gather(*tasks)
    await S3Write(os.environ["BUCKET_URI"])

asyncio.run(main())
