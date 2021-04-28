import asyncio, json
from mist.lang.streams import streams

async def wpscan(url, stack:list=None, commands:list=None):
    proc = await asyncio.create_subprocess_shell(f"wpscan --url {url} --detection-mode passive --format json", stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    parsedOutput = json.loads(stdout)
    if "targetStream" in stack[-1]:
        print("SEND", url)
        await streams.send(stack[-1]["targetStream"][0], parsedOutput)
    return parsedOutput
