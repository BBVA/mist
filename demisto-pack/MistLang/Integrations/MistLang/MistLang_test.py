"""Base Integration for Cortex XSOAR - Unit Tests file

Pytest Unit Tests: all funcion names must start with "test_"

More details: https://xsoar.pan.dev/docs/integrations/unit-testing

MAKE SURE YOU REVIEW/REPLACE ALL THE COMMENTS MARKED AS "TODO"

You must add at least a Unit Test function for every XSOAR command
you are implementing with your integration
"""


def test_baseintegration_dummy():
    """Tests helloworld-say-hello command function.

    Checks the output of the command function with the expected output.

    No mock is needed here because the say_hello_command does not call
    any external API.
    """
    from MistLang import Client, baseintegration_dummy_command

    client = Client(base_url='some_mock_url', verify=False)
    args = {
        'url': 'https://raw.githubusercontent.com/BBVA/mist/master/test/mist_files/done.mist'
    }
    response = baseintegration_dummy_command(client, **args)

    assert response == ("ok", {"url": args["url"], "output": "Hello\n"})
    

def test_baseintegration_dummy_404_url():
    """Tests helloworld-say-hello command function.

    Checks the output of the command function with the expected output.

    No mock is needed here because the say_hello_command does not call
    any external API.
    """
    from MistLang import Client, baseintegration_dummy_command

    client = Client(base_url='some_mock_url', verify=False)
    args = {
        'url': 'https://raw.githubusercontent.com/BBVA/mist/master/test/mist_files/not_existing.mist'
    }
    response = baseintegration_dummy_command(client, **args)

    assert response == ("network error", {"url": args["url"], "output": "404"})
    
def test_baseintegration_dummy_malformed_mist_file():
    """Tests helloworld-say-hello command function.

    Checks the output of the command function with the expected output.

    No mock is needed here because the say_hello_command does not call
    any external API.
    """
    from MistLang import Client, baseintegration_dummy_command

    client = Client(base_url='some_mock_url', verify=False)
    args = {
        'url': 'https://raw.githubusercontent.com/demisto/demisto-sdk/master/demisto_sdk/commands/init/README.md'
    }
    response = baseintegration_dummy_command(client, **args)

    assert response[0] == "mist file error"
    assert response[1]["url"] == args["url"]
