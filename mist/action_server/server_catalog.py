import sqlite3

from typing import List

from mist.sdk.db import cm
from mist.action_catalog.catalog import catalog_path


def get_server_catalog():

    def find_all_command_names(con) -> List[str]:
        q = "SELECT command FROM COMMANDS"
        with cm(con) as cursor:
            cursor.execute(q)
            return [x["command"] for x in cursor.fetchall()]

    def get_cheatsheet(con) -> List[dict]:
        q = """
        SELECT COMMANDS.id,command,description,tags,latest_version,catalog_id,uri FROM COMMANDS
        INNER JOIN CATALOG ON COMMANDS.catalog_id = CATALOG.id
        """
        with cm(con) as cursor:
            cursor.execute(q)
            return [dict(x) for x in cursor.fetchall()]

    catalog_db_path = str(catalog_path().joinpath("catalog.db"))
    sqlite_connection = sqlite3.connect(catalog_db_path)
    sqlite_connection.row_factory = sqlite3.Row

    commands = find_all_command_names(sqlite_connection)
    cheatsheet = get_cheatsheet(sqlite_connection)

    sqlite_connection.close()

    return commands, cheatsheet
