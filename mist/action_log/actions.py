import os
import sys
import json
import hashlib
import datetime
import argparse
from collections import namedtuple
from textwrap import wrap

from terminaltables import SingleTable

from mist.sdk import db, config, MistInputDataException
from mist.sdk.cmd import _DB_TABLE_NAME, _DB_TABLE_FIELDS

def load_cli_values(d, parsed: argparse.Namespace):
    d.update(parsed.__dict__)



def log_console(parsed: argparse.Namespace):
    #
    # Load console config
    #
    load_cli_values(config, parsed)

    #
    # Setup database
    #
    db.setup(f"sqlite3://{config.MIST_DB}")

    row_id = parsed.row_id
    db_query = f"select stdout, stderr, command from {_DB_TABLE_NAME} where ID = ?"

    if not(execution_details := db.fetch_one(db_query, (row_id,))):
        raise MistInputDataException(f"Row Id '{row_id}' doesn't exits")

    msg = " Original Console Output "
    print()
    print("-" * 30, msg , "-" * 30)
    print()
    print(f"$ {execution_details[2]}")
    print(execution_details[0])

    if execution_details[1]:
        print(execution_details[1])
    print("")
    print("-" * (62 + len(msg)))

def log_signature(parsed: argparse.Namespace):

    def check_signature(content: str or bytes, signature: str) -> bool:
        if not content and not signature:
            return True

        try:
            b_content = content.encode()
        except:
            b_content = content


        return hashlib.sha512(b_content).hexdigest() == signature

    def msg(message: str, ok: bool):
        print(f"[{'*' if ok else '!INVALID SIGNATURE!'}] {message}")

    #
    # Load console config
    #
    load_cli_values(config, parsed)

    #
    # Setup database
    #
    db.setup(f"sqlite3://{config.MIST_DB}")

    quiet = parsed.quiet
    signature_file = parsed.signature_file
    db_name = os.path.abspath(parsed.MIST_DB)

    db_query = f"select id, stdout, stdout_signature, " \
               f"stderr, stderr_signature from {_DB_TABLE_NAME}"

    total_fails = 0

    if signature_file:
        check = check_signature(
            open(db_name, "rb").read(),
            open(signature_file, "r").read()
        )

        if not check:
            total_fails += 1

        if not quiet:
            msg("Check database signature file", check)

    for row in db.fetch_many(db_query):
        row_id = row[0]
        stdout, stdout_signature = row[1:3]
        stderr, stderr_signature = row[3:5]

        check_stdout = check_signature(stdout, stdout_signature)
        check_stderr = check_signature(stderr, stderr_signature)

        if check_stderr or check_stdout:
            total_fails += 1

        if not quiet:
            msg(f"Checked register '{row_id}' :: console output", check_stdout)
            msg(f"Checked register '{row_id}' :: console error", check_stderr)

    if total_fails > 0:
        exit(1)

def log_details(parsed: argparse.Namespace):
    #
    # Load console config
    #
    load_cli_values(config, parsed)

    #
    # Setup database
    #
    db.setup(f"sqlite3://{config.MIST_DB}")

    db_name = os.path.basename(parsed.MIST_DB)

    row_id = parsed.row_id
    db_query = f"select * from {_DB_TABLE_NAME} where ID = ?"

    if not(execution_details := db.fetch_one(db_query, (row_id,))):
        raise MistInputDataException(f"Row Id '{row_id}' doesn't exits")

    table_content = []

    for i, field in enumerate(_DB_TABLE_FIELDS):
        content = execution_details[i + 1]

        if field in ("in_files", "out_files"):
            if _content := json.loads(content):
                files = []
                for x, y in _content.items():
                    f_path = '\n'.join(wrap(y.get('path', '')))
                    files.append(f"{x} -> {f_path}")

                content = "\n".join(wrap(" ".join(files), width=60, placeholder="..."))

            else:
                content = "-"

        else:
            if type(content) is str:
                content = "\n".join(wrap(content, width=60, placeholder="..."))

            if not content:
                content = "-"

        if field in ("start_time", "end_time"):
            content = datetime.datetime.fromtimestamp(float(content))

        table_content.append((
            field, content
        ))

    table = SingleTable(table_content,
                        title=f"Database '{db_name}' :: Row '{row_id}'")
    table.inner_row_border = True

    print("")
    print(table.table)
    print("")


def log_summary(parsed: argparse.Namespace):
    #
    # Load console config
    #
    load_cli_values(config, parsed)

    #
    # Setup database
    #
    db.setup(f"sqlite3://{config.MIST_DB}")

    db_name = os.path.basename(parsed.MIST_DB)

    content = []
    content.append(["ID", "Command", "Starts", "Ends"])

    for row in db.fetch_many(f"select * from {_DB_TABLE_NAME}"):
        start = datetime.datetime.fromtimestamp(float(row[2]))
        end = datetime.datetime.fromtimestamp(float(row[3]))

        r1 = row[1]

        if len(r1) > 30:
            r1= f"{r1[:30]}..."

        content.append([
            row[0],
            r1,
            start.strftime("%Y/%m/%d - %H:%M:%S:%f"),
            end.strftime("%Y/%m/%d - %H:%M:%S:%f")
        ])

    table = SingleTable(content, title=f"Execution logs for '{db_name}'")
    table.inner_row_border = True

    print("")
    print(table.table)
    print("")


