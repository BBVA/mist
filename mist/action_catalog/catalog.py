import os
import json

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import List

from mist.guuid import guuid
from mist.sdk.db import cm

from ..finders import find_commands_folders, find_catalog_metas
from ..net_utils import download, file_uri_to_path, git_clone
from ..sdk import MistException, config


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
        self._connection.row_factory = sqlite3.Row
        self.__create_catalog_database__(self._connection)

    def __create_catalog_database__(self, con):
        q = """
    CREATE TABLE IF NOT EXISTS CATALOG
    (
        id TEXT PRIMARY KEY, 
        uri text NULL, 
        local_path text,
        
        UNIQUE(uri)
    );
    CREATE INDEX IF NOT EXISTS idx_catalog_name ON CATALOG (uri);
     
    CREATE TABLE IF NOT EXISTS COMMANDS
    (
        id TEXT PRIMARY KEY, 
        command text, 
        description text,
        tags json, 
        latest_version text,
        
        catalog_id text NULL, 
        
        UNIQUE(command),
        
        FOREIGN KEY(catalog_id) REFERENCES CATALOG(id) ON DELETE CASCADE
    ); 
    CREATE INDEX IF NOT EXISTS idx_catalog_name ON COMMANDS (command);
    CREATE INDEX IF NOT EXISTS idx_catalog_description ON COMMANDS (description);

    CREATE TABLE IF NOT EXISTS COMMANDS_VERSIONS
    (
        id TEXT PRIMARY KEY, 
        version text, 
        command_path text,
        command_id TEXT,
        
        FOREIGN KEY(command_id) REFERENCES COMMANDS(id) ON DELETE CASCADE
    ); 
    CREATE INDEX IF NOT EXISTS idx_catalog_commands_version ON COMMANDS_VERSIONS (version);
    """
        with cm(con) as cursor:
            cursor.executescript(q)

    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection:
            self.__init_database__()

        return self._connection

    def _store_catalog(self,
                       uri: str,
                       path: str) -> str:
        catalog_id = guuid()

        q_catalog = """
        INSERT INTO CATALOG (id, uri, local_path)
        VALUES (?, ?, ?);
        """
        try:
            with cm(self.connection) as cursor:
                cursor.execute(q_catalog, (
                    catalog_id,
                    uri,
                    path
                ))

        except sqlite3.IntegrityError:
            q = "SELECT id from CATALOG WHERE uri = ?"
            with cm(self.connection) as cursor:
                cursor.execute(q, (uri,))
                catalog_id = cursor.fetchone()["id"]

        return catalog_id

    def _store_command(self,
                       cmd_name: str,
                       cmd_description: str,
                       cmd_tags: str,
                       cmd_latest: str,
                       catalog_id: str) -> str:
        """Add new command to catalog and return their DB Id"""
        command_id = guuid()

        q_catalog = """
        INSERT INTO COMMANDS (id, command, description, tags, latest_version, 
        catalog_id)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with cm(self.connection) as cursor:
                cursor.execute(q_catalog, (
                    command_id,
                    cmd_name,
                    cmd_description,
                    cmd_tags,
                    cmd_latest,
                    catalog_id
                ))

        except sqlite3.IntegrityError:
            q = "SELECT id from COMMANDS WHERE command = ?"
            with cm(self.connection) as cursor:
                cursor.execute(q, (cmd_name,))
                command_id = cursor.fetchone()["id"]


        return command_id

    def _store_command_version(self,
                               command_id: str,
                               version: str,
                               path: str) -> str:
        """Add new version for a command and return their DB id"""
        version_id = guuid()

        q_versions = """
        INSERT INTO COMMANDS_VERSIONS (id, version, command_path, command_id)
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


    def _index_catalog(self, new_catalog_path: str, catalog_uri: str = None):

        if not catalog_uri:
            catalog_uri = new_catalog_path

        catalog_id = self._store_catalog(catalog_uri, str(new_catalog_path))

        for (command_path, index_content) in find_commands_folders(
                new_catalog_path
        ):

            versions = {}
            for version_path, meta_content in find_catalog_metas(command_path):
                versions[meta_content["version"]] = version_path

            #
            # Insert catalog indexes
            #
            try:
                cmd_name = index_content["name"]
            except KeyError:
                raise ValueError("Command INDEX file must has 'name' property")

            try:
                cmd_latest = index_content["latest"]
            except:
                raise ValueError(
                    "Command INDEX file must has 'latest' property")

            try:
                cmd_description = index_content["description"]
            except:
                raise ValueError(
                    "Command INDEX file must has 'description' property")

            if tags := index_content.get("tags", None):
                cmd_tags = json.dumps([
                    x.strip()
                    for x in tags.split(",")
                ])
            else:
                cmd_tags = json.dumps([])

            command_id = self._store_command(
                cmd_name,
                cmd_description,
                cmd_tags,
                cmd_latest,
                catalog_id
            )

            #
            # Insert catalog versions
            #
            for version, path in versions.items():
                self._store_command_version(
                    command_id, version, path
                )


    def find_command(self, name: str, version: str) -> dict or None:
        if commands := self.find_all_commands(name, version):
            return commands[0]

    def find_all_commands(self, name: str = None, version: str = None) -> List[dict] or None:
        """
        If we want to get all latest version of commands we must set version to
        'latest'
        """

        q = """
        SELECT COMMANDS_VERSIONS.command_path FROM COMMANDS_VERSIONS
        INNER JOIN COMMANDS ON COMMANDS.id = COMMANDS_VERSIONS.command_id
        """

        args = []
        if name or version:
            if name:

                q = f"""
                    {q}
                    WHERE COMMANDS.command = ?
                    """
                args.append(name)

                if version == "latest":
                    q = f"""
                    {q} AND COMMANDS.latest_version = COMMANDS_VERSIONS.version"
                    """
                else:
                    q = f"""
                    {q} AND COMMANDS_VERSIONS.version = ?
                    """
                    args.append(version
                                )

        with cm(self.connection) as cursor:
            cursor.execute(q, args)

            return [dict(x) for x in cursor.fetchall()]

    def find_catalog(self,
                     *,
                     catalog_uri: str = None,
                     catalog_id: str = None) -> List[dict]:

        q_catalog = """
        SELECT * FROM CATALOG 
        """

        values = []
        if catalog_uri or catalog_id:
            q_catalog = f"{q_catalog} WHERE "

            if catalog_uri:
                q_catalog = f"{q_catalog} uri = ?"
                values.append(catalog_uri)

            if catalog_id:
                q_catalog = f"{q_catalog} id = ?"
                values.append(catalog_id)

        with cm(self.connection) as cursor:
            cursor.execute(q_catalog, values)
            return cursor.fetchall()


    def add_catalog(self, catalog_uri: str):

        git_providers = {
            "https://github.com",
            "https://gitlab.com",
            "https://bitbucket.org",
        }

        #
        # Import remote catalog
        #

        # Check if is a git repository
        catalog_dst = None
        if catalog_uri.startswith("http"):
            if any(p in catalog_uri for p in git_providers):

                # Remove first "/"
                dst = str(
                    file_uri_to_path(catalog_uri)
                ).replace(".git", "")[1:]

                catalog_dst = catalog_path().joinpath(dst)

                if not catalog_dst.exists():
                    catalog_dst.mkdir(parents=True)

                if not config.get("quiet", False):
                    print("[*] Downloading core catalog...", end='',
                          flush=True)

                git_clone(catalog_uri, str(catalog_dst))

                if not config.get("quiet", False):
                    print("Done", flush=True)

            # Check if is a remote web
            else:
                catalog_dst = str(file_uri_to_path(catalog_uri)).replace(
                    ".git", "")[1:]

                try:
                    download(catalog_uri, catalog_dst)
                except Exception as e:
                    MistException(
                        f"Error while try to download catalog: '{catalog_uri}'"
                    )

        # Checks if is path existing path
        elif os.path.exists(catalog_uri):

            raise NotImplementedError(
                "Currently only supported catalogs from GIT repositories"
            )
            # TODO: check catalog_dst

        else:
            raise MistException(
                "Can't find catalog. If you are trying to add a remote catalog"
                "it must starts as 'http://' or 'https://'"
            )

        self._index_catalog(catalog_dst, catalog_uri)

    def reindex(self):
        for catalog in os.listdir(catalog_path()):

            _path = str(catalog_path().joinpath(catalog))

            if not os.path.isdir(_path):
                continue

            self._index_catalog(_path)

    def search(self, query: str):

        q = """
        SELECT COMMANDS.command, COMMANDS.description, COMMANDS.tags, COMMANDS.latest_version 
        FROM COMMANDS
        WHERE COMMANDS.command like ? or COMMANDS.description like ? 
        """

        params = f"%{query}%"

        with cm(self.connection) as cursor:
            cursor.execute(q, (params, params))

            return [dict(x) for x in cursor.fetchall()]

    def delete_catalog(self, catalog_id: str) -> int:

        q = """
        DELETE FROM CATALOG 
        WHERE CATALOG.id = ?
        """

        with cm(self.connection) as cursor:
            cursor.execute(q, (catalog_id,))

            return cursor.rowcount


Catalog = _Catalog()


__all__ = ("Catalog",)
