import asyncio

async def searchDomains(domain, q):
    domains = []
    proc = await asyncio.create_subprocess_shell(f"dnsrecon -d {domain} -t crt", stdout=asyncio.subprocess.PIPE)
    line = True
    while line:
        line = (await proc.stdout.readline()).decode('utf-8')
        fields = line.split()
        if len(fields)>1 and fields[1]=="A":
            if q:
                await q.put(fields[2])
            domains.append(fields[2])
    return domains

async def findOpenPorts(ip, ports, q):
    openPorts = []
    proc = await asyncio.create_subprocess_shell(f"nmap -p {ports} --open {ip}",stdout=asyncio.subprocess.PIPE)
    line = True
    while line:
        line = (await proc.stdout.readline()).decode('utf-8')
        fields = line.split()
        if len(fields)>1 and fields[1]=="open":
            openPort = fields[0].split("/")
            if q:
                await q.put({"ip": ip, "port": openPort[0], "protocol": openPort[1]})
            openPorts.append({"port": openPort[0], "protocol": openPort[1]})
    return openPorts
