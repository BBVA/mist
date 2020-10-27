from mist.sdk import run_in_mist_server

playbook = """
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
    ret = run_in_mist_server(
        "http://localhost:9000",
        playbook,
        {"target": "127.0.0.1"}
    )

    print(ret)


if __name__ == '__main__':
    main()
