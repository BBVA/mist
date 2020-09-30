import sqlite3

from typing import List
from functools import lru_cache
from contextlib import contextmanager

from .config import config

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
        self._connection = None
        self._connection_string: str = ""
        self.database_type: str = "sqlite"

    @property
    def connection(self):
        if not self._connection:
            if not self._connection_string:
                self._connection = sqlite3.connect(":memory:")

            elif self._connection_string.startswith("sqlite3://"):
                _cs = self._connection_string.replace("sqlite3://", "")
                self._connection = sqlite3.connect(_cs)

            else:
                raise ValueError("Invalid database connection string")

        return self._connection

    def setup(self, connection_string: str):
        self._connection_string = connection_string

    @lru_cache(50)
    def tbl_name(self, name: str) -> str:
        # TODO: not deleted because we don't know if we'll need in the future
        return name

    def create_table(self,
                     table_name: str,
                     table_fields: tuple):

        query = f'''
        CREATE TABLE {self.tbl_name(table_name)} 
        (id integer PRIMARY KEY AUTOINCREMENT, {', '.join(table_fields)})
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

    def insert(self, table: str, values: List[str], *, fields=None):
        query = f'''
        INSERT INTO {self.tbl_name(table)}
        {f"({', '.join(fields)})" if fields else ''}
        VALUES ({'' if fields else 'null,'} {', '.join(['?' for _ in range(len(values))])})
        '''

        with cm(self.connection) as cur:
            cur.execute(query, values)

    def fetch_one(self, query: str) -> tuple:

        with cm(self.connection) as cur:
            cur.execute(query)
            return cur.fetchone()

    def fetch_many(self, query: str) -> List[tuple]:

        with cm(self.connection) as cur:
            cur.execute(query)
            return cur.fetchall()

    @lru_cache(50)
    def fetch_table_headers(self, table:str) -> List[tuple]:
        schema = self.fetch_many(f"PRAGMA table_info({self.tbl_name(table)});")

        return [
            s[1] for s in schema
        ]


    def fetch_table_as_dict(self, table: str) -> List[dict]:
        table_headers = self.fetch_table_headers(self.tbl_name(table))
        table_data = self.fetch_many(f"SELECT * FROM {self.tbl_name(table)}")

        return [
            dict(zip(table_headers, tuple))
            for tuple in table_data
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

db = _DB()

__all__ = ("db")
