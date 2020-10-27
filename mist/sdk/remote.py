import json
import time
import urllib.request
import os.path as op


def run_in_mist_server(server: str,
                       playbook: str,
                       parameters: dict = None) -> str:
    """
    This function runs a playbook in a remote MIST server
    """
    if not server.startswith("http"):
        raise ValueError("'server' must starts with 'http://' or 'https://'")
    if server.endswith("/"):
        server = server[:-1]

    if op.exists(playbook):
        with open(playbook, "r") as f:
            content = f.read()
    elif playbook.startswith("http"):
        content = urllib.request.Request(playbook).read()

        try:
            content = content.decode()
        except AttributeError:
            pass

    else:
        content = playbook

    if parameters:
        if type(parameters) is not dict:
            raise ValueError("Parameters must be a dict")

    req = urllib.request.Request(f"{server}/run")
    req.add_header('Content-Type', 'application/json')

    response = urllib.request.urlopen(
        req,
        data=json.dumps({
            "content": content,
            "parameters": {"target": "127.0.0.1"}
        }).encode()
    )

    try:
        jobId = json.loads(response.read().decode())["jobId"]
    except Exception as e:
        return f"Error: {str(e)}"

    #
    # Wait for ending
    #
    while 1:
        response = urllib.request.urlopen(
            f"{server}/run/{jobId}/status"
        )
        status = json.loads(response.read().decode())["status"]

        if status == "finished":
            break
        else:
            time.sleep(1)

    #
    # Download report
    #
    response = urllib.request.urlopen(
        f"{server}/run/{jobId}"
    )
    return json.loads(
        response.read().decode()
    ).get("message", "")

__all__ = ("run_in_mist_server",)
