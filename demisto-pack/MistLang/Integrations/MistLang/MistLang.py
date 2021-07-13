import requests
from typing import Dict, Any, List, Union, Tuple, Any, Optional
from mist.action_run import execute_from_text
from mist.lang.config import config
import asyncio, json
from zipfile import ZipFile
from io import BytesIO
import os

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member


''' CONSTANTS '''

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # ISO8601 format with UTC, default in XSOAR

''' CLIENT CLASS '''


class Client():
    def __init__(self, base_url, verify):
        self.base_url = base_url
        self.verify = verify

    def baseintegration_dummy(self, url, params) -> Tuple[str, dict]:
        #TODO: download from git repo
        req = requests.get(url)
        if req.status_code == 200:
            try:
                if url.endswith(".zip"):
                    zipfile = ZipFile(BytesIO(req.content))
                    zipfile.extractall("./mist_tmp_zip")
                    os.chdir('./mist_tmp_zip')
                    with open("main.mist") as f:
                        mist_content = f.read()
                else:
                    mist_content = req.content.decode("utf-8", "ignore")
                output = asyncio.run(execute_from_text(mist_content, fn_params=params))
                result = {"url": url, "raw_output": output}
                try:
                    output_json = json.loads(output)
                    for k,v in output_json.items():
                        result[k] = v
                except:
                    pass
                return "ok", result
            except Exception as e:
                return "mist file error", {"url": url, "output": str(e)}
            finally:
                if os.path.abspath(os.path.curdir).endswith("mist_tmp_zip"):
                    os.chdir('..')
                    os.system("rm -rf ./mist_tmp_zip")
        return "network error", {"url": url, "output": str(req.status_code)}


''' HELPER FUNCTIONS '''


''' COMMAND FUNCTIONS '''


def test_module(client: Client) -> str:
    message: str = ''
    try:
        # TODO: ADD HERE some code to test connectivity and authentication to your service.
        # This  should validate all the inputs given in the integration configuration panel,
        # either manually or by using an API that uses them.
        message = 'ok'
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):  # TODO: make sure you capture authentication errors
            message = 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return message


def baseintegration_dummy_command(client: Client, url, params = "") -> Tuple[str, dict]: #CommandResults:
    if not url:
        raise ValueError('url not specified')

    params_dict = {}
    if params:
        try:
            params_json = json.loads(params)
            for p in params_json:
                f = p.strip().split("=")
                params_dict[f[0].strip()] = f[1].strip()
        except:
            raise ValueError('Malformed params.')

    # Call the Client function and get the raw response
    result = client.baseintegration_dummy(url, params_dict)

    # return CommandResults(
    #     outputs_prefix='BaseIntegration',
    #     outputs_key_field='',
    #     outputs=result,
    # )
    #return "BaseIntegration.Output", {}, result
    return result
    
# TODO: ADD additional command functions that translate XSOAR inputs/outputs to Client


''' MAIN FUNCTION '''

def main():
    params = demisto.params() # Lo de la seccion de configuracion. Estos es la comnfigutacion de la instancia
    args = demisto.args() # Argumentos de la integracion (playbook)
    command = demisto.command() # El nombre del comando (playbook)
    client = Client(
        "",
        False
        #argToList(params.get('urls')),
        # params.get('credentials', {}).get('identifier'),
        # params.get('credentials', {}).get('password'),
        # params['database'],
        # bool(params.get('use_ssl', False)),
        # bool(params.get('insecure', False))
    )
    commands = {
        'test-module': test_module,
        'baseintegration-dummy': baseintegration_dummy_command
    }
    try:
        return_outputs(*commands[command](client, **args))  # type: ignore[operator]
    except Exception as e:
        return_error(f'MistLang: {str(e)}', error=e)


''' ENTRY POINT '''
if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
