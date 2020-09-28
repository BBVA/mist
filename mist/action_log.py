import os
import argparse
import datetime

from terminaltables import SingleTable

from mist.sdk import db
from mist.sdk.cmd import _DB_TABLE_NAME, _DB_TABLE_FIELDS

def do_log(config: argparse.Namespace):

    db_name = os.path.basename(config.MIST_DB)

    content = []
    content.append(["ID", "Command", "Starts", "Ends"])

    for row in db.fetch_many(f"select * from {_DB_TABLE_NAME}"):
        start = datetime.datetime.fromtimestamp(float(row[2]))
        end = datetime.datetime.fromtimestamp(float(row[3]))

        content.append([
            row[0],
            row[1],
            start.strftime("%Y/%m/%d - %H:%M:%S:%f"),
            end.strftime("%Y/%m/%d - %H:%M:%S:%f")
        ])

    table = SingleTable(content, title=f"Execution logs for '{db_name}'")
    table.inner_row_border = True

    print("")
    print(table.table)
    print("")


