import json
import urllib.request

content = """
# Name: Ping
# Tags: ping, network
# Description: Ping some host

ping {
    version <= "1.0.0"
    input {
        ip <= %target
    }
    output {
        result
        console
    }
    then {
        check result is Success {
            print "Remote host responds"
        }
        check result is Error {
            print "Remote host not responds"
        }
    }
}
"""

def main():
    req = urllib.request.Request("http://localhost:9000/run")
    req.add_header('Content-Type', 'application/json')

    response = urllib.request.urlopen(
        req,
        data=json.dumps({
            "content": content,
            "parameters": {"target": "127.0.0.1"}
        }).encode()
    )

    print(json.loads(response.read().decode()))


if __name__ == '__main__':
    main()
