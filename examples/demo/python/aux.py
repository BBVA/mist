import sys, asyncio, inspect

done = 0

async def producer(f, *args):
    await f(*args)
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
