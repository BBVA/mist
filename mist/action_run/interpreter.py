import sys
import builtins
import asyncio

from io import StringIO
from contextlib import redirect_stdout
from typing import Callable

from mist.sdk import (db, config, params, command_runner, functions)

from .language_tools import get_mist_model, load_mist_language, \
    check_mist_parameters, check_installed_binaries

from mist.lang.streams import consumers, producers
from mist.sdk.cmd import interactive_processes

async def waitForTaks():
    if len(producers)>0:
        await asyncio.gather(*producers)
    if len(consumers)>0:
        await asyncio.gather(*consumers)
    for i in interactive_processes:
        await i[0].finish_run(i[1],i[2], False)

def execute():
    try:
        asyncio.run(execute_aux())
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass

async def execute_aux():
    mist_model = get_mist_model()

    if config.simulate:
        print("[*] File loaded successfully")
    else:
        # Run user program!
        stack = [{ }]
        await command_runner(mist_model.commands, stack)
        await waitForTaks()
        await runFinalizers(stack)


async def execute_from_text(text: str,
                      fn_params: dict = None,
                      realtime_fn: Callable = None,
                      waitTime:int = 0,
                      stack: list = [{ }],
                      **kwargs) -> str:
    if fn_params:
        params.update(fn_params)

    if kwargs:
        config.update(kwargs)

    # Set config defaults
    default_configs = {
        "console_output": True,
        "real_time": True,
        "debug": False,
        "database_path": None,
        "simulate": False,
        "no_check_tools": False
    }

    if db_path := kwargs.get("database_path", None):
        db.setup(f"sqlite3://{db_path}")
    else:
        db.setup()

    #
    # Overwrite print buildin function to send each print(...) line to
    # callback too
    #
    if realtime_fn:
        def real_time_print(*args, **kwargs):
            sep = kwargs.get("sep", " ")
            end = kwargs.get("end", "\n")
            _file = kwargs.get("file", sys.stdout)

            msg = f"{sep.join(str(x) for x in args)}{end}"
            try:
                realtime_fn(msg)
            except Exception as e:
                pass

            _file.write(msg)
            _file.flush()

        builtins.print = real_time_print


    if need_config := set(default_configs.keys()) - set(kwargs.keys()):
        for c in need_config:
            config[c] = default_configs[c]

    mist_meta_model = load_mist_language(text)

    stream_stdout = StringIO()
    write_to_output = redirect_stdout(stream_stdout)

    with write_to_output:
        mist_model = mist_meta_model.model_from_str(text)

        # Check installed binaries
        check_installed_binaries(mist_model)

        # Check needed parameters for .mist
        check_mist_parameters(text)

        await command_runner(mist_model.commands, stack)
        if waitTime:
            await asyncio.sleep(waitTime)
        else:
            await waitForTaks()
        
        await runFinalizers(stack)

    return stream_stdout.getvalue()


async def runFinalizers(stack):
    if "finallyHook" in functions:
        await command_runner(functions["finallyHook"]["commands"], stack)


__all__ = ("execute", "execute_from_text")
