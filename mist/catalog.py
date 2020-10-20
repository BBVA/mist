import os

import sqlite3
from functools import lru_cache
from pathlib import Path

from mist.guuid import guuid
from mist.sdk.db import cm
from mist.action_catalog.repositories import CORE_CATALOG

@lru_cache
def catalog_path() -> Path:
    mist_home = Path().home().joinpath(".mist")

    if not mist_home.exists():
        mist_home.mkdir()

    return mist_home.joinpath("catalog")

class _Catalog():

    def __init__(self):
        self.db_path = str(catalog_path().joinpath("catalog.db"))
        self._connection = None

    def __init_database__(self):
        self._connection = sqlite3.connect(self.db_path)
        self.__create_catalog_database__(self._connection)

    def __create_catalog_database__(self, con):
        q = """
    CREATE TABLE IF NOT EXISTS CATALOG
    (
        id TEXT PRIMARY KEY, 
        origin text NULL, 
        command text, 
        description text,
        tags json, 
        latest_version text,
        
        UNIQUE(command)
    ); 
    CREATE INDEX IF NOT EXISTS idx_catalog_name ON CATALOG (command);
    CREATE INDEX IF NOT EXISTS idx_catalog_description ON CATALOG (description);

    CREATE TABLE IF NOT EXISTS CATALOG_COMMANDS
    (
        id TEXT PRIMARY KEY, 
        version text, 
        command_path text,
        command_id TEXT,
        FOREIGN KEY(command_id) REFERENCES CATALOG(id)
    ); 
    CREATE INDEX IF NOT EXISTS idx_catalog_commands_version ON CATALOG_COMMANDS (version);
    """
        with cm(con) as cursor:
            cursor.executescript(q)

    def add_command(self,
                    cmd_name: str,
                    cmd_description: str,
                    cmd_tags: list,
                    cmd_latest: str,
                    catalog_origin: str = None) -> str:
        """Add new command to catalog and return their DB Id"""
        catalog_id = guuid()

        q_catalog = """
        INSERT INTO CATALOG (id, command, description, tags, latest_version, 
        origin)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with cm(self.connection) as cursor:
                cursor.execute(q_catalog, (
                    catalog_id,
                    cmd_name,
                    cmd_description,
                    cmd_tags,
                    cmd_latest,
                    catalog_origin
                ))
        except sqlite3.IntegrityError:
            print(f"command {cmd_name} already exits")
            pass

        return catalog_id

    def add_command_version(self,
                            command_id: str,
                            version: str,
                            path: str) -> str:
        """Add new version for a command and return their DB id"""
        version_id = guuid()

        q_versions = """
        INSERT INTO CATALOG_COMMANDS (id, version, command_path, command_id)
        VALUES (?, ?, ?, ?);
        """

        with cm(self.connection) as cursor:
            cursor.execute(q_versions, (
                version_id,
                version,
                path,
                command_id
            ))

        return version_id

    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection:
            self.__init_database__()

        return self._connection

    def find_command(self, name: str, version: str = None) -> str:

        if version:
            q = """
            SELECT CATALOG_COMMANDS.command_path FROM CATALOG_COMMANDS
            INNER JOIN CATALOG ON CATALOG.id = CATALOG_COMMANDS.command_id
            WHERE CATALOG_COMMANDS.version = ? AND CATALOG.command = ?;
            """
            args = (name, version)

        else:
            q = """
            SELECT CATALOG_COMMANDS.command_path FROM CATALOG_COMMANDS
            INNER JOIN CATALOG ON CATALOG.id = CATALOG_COMMANDS.command_id
            WHERE CATALOG.latest_version = CATALOG_COMMANDS.version AND CATALOG.command = ?;
            """

            args = (name,)

        with cm(self.connection) as cursor:
            cursor.execute(q, args)
            return cursor.fetchone()



Catalog = _Catalog()


__all__ = ("Catalog",)
