import asyncio, json
from mist.lang.streams import streams

async def wpscan(url, stack:list=None, commands:list=None):
    proc = await asyncio.create_subprocess_shell(f"wpscan --url {url} --detection-mode passive --format json", stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    parsedOutput = json.loads(stdout)    
    r = {
        "resultCode": proc.returncode,
        "result": proc.returncode == 0,
        "consoleOutput": stdout.decode('utf-8'),
        "wpinfo": parsedOutput
    }
    if "targetStream" in stack[-1]:
        await streams.send(stack[-1]["targetStream"][0], r)
    return r
