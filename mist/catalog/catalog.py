import json
import os
import shutil

import sqlite3
from functools import lru_cache
from pathlib import Path

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

    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection:
            self.__init_database__()

        return self._connection

    def store_command(self,
                      cmd_name: str,
                      cmd_description: str,
                      cmd_tags: str,
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

    def store_command_version(self,
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


    def find_command(self, name: str, version: str = None) -> str or None:

        if version:
            q = """
            SELECT CATALOG_COMMANDS.command_path FROM CATALOG_COMMANDS
            INNER JOIN CATALOG ON CATALOG.id = CATALOG_COMMANDS.command_id
            WHERE CATALOG_COMMANDS.version = ? AND CATALOG.command = ?;
            """
            args = (version, name)

        else:
            q = """
            SELECT CATALOG_COMMANDS.command_path FROM CATALOG_COMMANDS
            INNER JOIN CATALOG ON CATALOG.id = CATALOG_COMMANDS.command_id
            WHERE CATALOG.latest_version = CATALOG_COMMANDS.version AND CATALOG.command = ?;
            """

            args = (name,)

        with cm(self.connection) as cursor:
            cursor.execute(q, args)

            if ret := cursor.fetchone():
                return ret[0]

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

            # TODO: check catalog_dst
            shutil.copy(catalog_uri, catalog_path())

        else:
            raise MistException(
                "Can't find catalog. If you are trying to add a remote catalog"
                "it must starts as 'http://' or 'https://'"
            )

        return catalog_dst

    def index_catalog(self, new_catalog_path: str = None, catalog_origin: str = None):

        for (command_path, index_content) in find_commands_folders(
                new_catalog_path):

            versions = {}
            for version_path, meta_content in find_catalog_metas(command_path):
                versions[meta_content["version"]] = version_path

                #
                # Insert catalog indexes
                #
                try:
                    cmd_name = meta_content["name"]
                except KeyError:
                    raise ValueError("Command INDEX file must has 'name' property")

                try:
                    cmd_latest = meta_content["latest"]
                except:
                    raise ValueError(
                        "Command INDEX file must has 'latest' property")

                try:
                    cmd_description = meta_content["description"]
                except:
                    raise ValueError(
                        "Command INDEX file must has 'description' property")

                if tags := meta_content.get("tags", None):
                    cmd_tags = json.dumps([
                        x.strip()
                        for x in tags.split(",")
                    ])
                else:
                    cmd_tags = json.dumps([])

                if not catalog_origin:
                    catalog_origin = "local"

                command_id = self.store_command(
                    cmd_name,
                    cmd_description,
                    cmd_tags,
                    cmd_latest,
                    catalog_origin
                )

                #
                # Insert catalog versions
                #
                for version, path in versions.items():
                    self.store_command_version(
                        command_id, version, path
                    )


Catalog = _Catalog()


__all__ = ("Catalog",)
