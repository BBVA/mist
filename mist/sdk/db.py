import json
import sqlite3
import hashlib
import os
import sys
from datetime import datetime, timezone

from typing import List
from functools import lru_cache
from contextlib import contextmanager

from ..guuid import guuid
from .config import config
from .exceptions import MistUndefinedVariableException

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives.serialization import pkcs12

@contextmanager
def cm(connection) -> sqlite3.Cursor:
    cur = connection.cursor()
    try:
        yield cur
    finally:
        connection.commit()
        cur.close()

class _DB:

    def __init__(self):
        self.connection = None
        self._connection_string: str = ""
        self.db_path: str = None
        self.database_type: str = "sqlite"

    def setup(self, connection_string: str = None):
        self._connection_string = connection_string

        if not self._connection_string:
            self.connection = sqlite3.connect(":memory:")

        elif self._connection_string.startswith("sqlite3://"):
            self.db_path = self._connection_string.replace(
                "sqlite3://", ""
            )
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )

        else:
            raise ValueError("Invalid database connection string")

    @lru_cache(50)
    def tbl_name(self, name: str) -> str:
        # TODO: not deleted because we don't know if we'll need in the future
        return name

    def create_table(self,
                     table_name: str,
                     table_fields: tuple):

        query = f'''
        CREATE TABLE {self.tbl_name(table_name)}
        (id blob(16) PRIMARY KEY NOT NULL, {', '.join(table_fields)})
        '''

        with cm(self.connection) as cur:
            try:
                cur.execute(query)
            except Exception as e:
                if config.debug:
                    print(f"[!] Error while creating database: {e}")

    def execute(self, query: str):
        with cm(self.connection) as cur:
            cur.execute(query)

    def update(self, row_id: str, table: str, values: dict):
        """returns last row id inserted"""
        query = f'''
        UPDATE {self.tbl_name(table)}
        SET
            {", ".join(f'{x} = ?' for x in values.keys())}
        WHERE id = "{row_id}"
        '''

        with cm(self.connection) as cur:
            res = cur.execute(query, list(values.values()))
            return res.rowcount

    def insert(self,
               table: str,
               values: List[str],
               *,
               fields: List[str] = None) -> str:
        """returns last row id inserted"""
        row_id = guuid()

        if fields:
            fields = ["id", *fields]
            sql_fields = f"({', '.join(fields)})" if fields else ''

        else:
            sql_fields = ""

        values = [row_id, *values]

        query = f'''
        INSERT INTO {self.tbl_name(table)} {sql_fields}
        VALUES ({', '.join(['?' for _ in range(len(values))])})
        '''

        with cm(self.connection) as cur:
            res = cur.execute(query, values)
            return row_id

    def fetch_one(self, query: str, values: list = None) -> tuple:

        with cm(self.connection) as cur:
            if values:
                cur.execute(query, values)
            else:
                cur.execute(query)

            return cur.fetchone()

    def fetch_many(self, query: str, values: list = None) -> List[tuple]:

        with cm(self.connection) as cur:
            if values:
                cur.execute(query, values)
            else:
                cur.execute(query)

            return cur.fetchall()

    @lru_cache(50)
    def fetch_table_headers(self, table:str) -> List[tuple]:
        schema = self.fetch_many(f"PRAGMA table_info({self.tbl_name(table)});")

        return [
            s[1] for s in schema
        ]

    def fetch_table_as_dict(self, table: str) -> List[dict]:
        try:
            table_headers = self.fetch_table_headers(self.tbl_name(table))
            table_data = self.fetch_many(f"SELECT * FROM {self.tbl_name(table)}")
        except sqlite3.OperationalError:
            raise MistUndefinedVariableException(table)
        transformed_table_data = []
        for t in table_data:
            row = []
            for f in t:
                if type(f) is str and f.startswith("[") and f.endswith("]"):
                    row.append(json.loads(f))
                else:
                    row.append(f)
            transformed_table_data.append(row)
        return [
            dict(zip(table_headers, tuple))
            for tuple in transformed_table_data
        ]

    def clean_database(self):
        def _drop_database_sqlite():
            q = "SELECT name FROM sqlite_master WHERE type='table';"
            for table in self.fetch_many(q):
                _table = table[0]

                if any(x in _table for x in ("sqlite", "execution")):
                    continue

                self.execute(f"DROP TABLE IF EXISTS {_table}")


        if self.database_type == "sqlite":
            if self._connection:
                _drop_database_sqlite()

    @lru_cache(1)
    def signature(self):
        hash = hashlib.sha512()
        with open(self.db_path, "rb") as f:
            hash.update(f.read())

        return hash.hexdigest()

    def sign(self, pkcs12_path=None, passphrase=None):
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self.db_path:
            return None

        if not os.path.isfile(self.db_path):
            raise Exception(f"Database file not found: {self.db_path}")

        if pkcs12_path is not None and not os.path.isfile(pkcs12_path):
            raise Exception(f"PKCS#12 file not found: {pkcs12_path}")

        hAlg = hashes.SHA256()
        hasher = hashes.Hash(hAlg)
        with open(self.db_path, "rb") as f:
            hasher.update(f.read())

        digest = hasher.finalize()

        document = {"URI": self.db_path, "tsDoc": {"ts": timestamp, "digest": digest.hex()}, "signCert": None, "signAlg": None, "signature": None}

        if pkcs12_path is not None:
            # Generate signature for tsDoc document
            # First open pkcs file and load certificate and private key
            if passphrase is None:
                bPass = None
            else :
                bPass = bytes(passphrase, "utf-8")

            with open(pkcs12_path, "rb") as f:
                p12 = pkcs12.load_key_and_certificates(f.read(), bPass)

            priv_key = p12[0]       # Private key
            certificate = p12[1]    # Certificate
            msg = json.dumps(document["tsDoc"])

            signature = priv_key.sign(bytes(msg, "utf-8"),
                                        padding.PSS(
                                                    mgf=padding.MGF1(hAlg),
                                                    salt_length=padding.PSS.MAX_LENGTH
                                        ),
                                        hAlg
                                     )

            document["signAlg"] = "SHA256WithRSASignature"
            document["signature"] = signature.hex()
            document["signCert"] = ""

        return json.dumps(document)

    def get_tables(self, cur, master):
        cur.execute(f"SELECT name FROM {master} WHERE type='table';")
        new_tables = []
        for table_item in cur.fetchall():
            new_tables.append(table_item[0])
        return new_tables

    def merge(self, dbfile):
        with cm(self.connection) as cur:
            cur.execute("ATTACH DATABASE ? AS newdb", (dbfile,))
            new_tables = self.get_tables(cur, "newdb.sqlite_master")
            old_tables = self.get_tables(cur, "sqlite_master")
            for table in new_tables:
                if table in old_tables:
                    cur.execute(f"INSERT INTO {table} SELECT * FROM newdb.{table};")
                    self.connection.commit()
                    # for row in cur.execute(f"SELECT * FROM newdb.{table}"):
                    #     q = f"INSERT INTO {table} VALUES ({','.join(["?" for i in row])});"
                    #     cur.execute(q,row)
                    #     self._connection.commit()
                else:
                    cur.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM newdb.{table}")
                    self.connection.commit()
            cur.execute("DETACH newdb")


db = _DB()

__all__ = ("db")
