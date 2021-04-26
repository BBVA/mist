import asyncio, json, tempfile

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

kafka_proc = None
async def kafkaProducer(message, servers, topic):
    global kafka_proc
    if not kafka_proc:
        kafka_proc = await asyncio.create_subprocess_shell(f"kafka-console-producer --broker-list {servers} --topic {topic}",
            stdout=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)
    message = json.dumps(message)
    kafka_proc.stdin.writelines([bytes(message+"\n", 'utf-8')])
    
async def festin(originDomain, dns, useTor, q):
    domains = []
    tor = ""
    if useTor:
        tor = "--tor"
    proc = await asyncio.create_subprocess_shell(f"festin {originDomain} {tor} -ds {dns}", stdout=asyncio.subprocess.PIPE)
    line = True
    while line:
        line = (await proc.stdout.readline()).decode('utf-8')
        if "Adding" in line:
            fields = line.split()
            r = fields[7][1:-1]
            if q:
                await q.put(r)
            domains.append(r)
    return domains

values = []
async def filterRepeated(v, q):
    global values
    if not v in values:
        values.append(v)
        await q.put(v)

localPath = False
async def S3Store(text):
    global localPath
    if not localPath:
        localPath = tempfile.NamedTemporaryFile(delete=False).name
    with open(localPath, 't+a') as f:
        f.write(str(text) + '\n')

async def S3Write(remoteUri):
    await asyncio.create_subprocess_shell(f"aws s3 cp '{localPath}' {remoteUri}", stdout=asyncio.subprocess.PIPE)

