import sqlite3

from typing import List
from contextlib import contextmanager

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
        self.connection = sqlite3.connect(':memory:')

    def create_table(self,
                     table_name: str,
                     table_fields: tuple):
        query = f'''
        CREATE TABLE {table_name} 
        (id integer PRIMARY KEY AUTOINCREMENT, {', '.join(table_fields)})
        '''

        with cm(self.connection) as cur:
            cur.execute(query)

    def execute(self, query: str):
        with cm(self.connection) as cur:
            cur.execute(query)

    def insert(self, table: str, values: List[str], *, fields=None):
        query = f'''
        INSERT INTO {table}
        {f"({', '.join(fields)})" if fields else '' }
        VALUES (null, {', '.join(['?' for _ in range(len(values))])})
        '''
        # VALUES ({', '.join(values)})
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


db = _DB()

__all__ = ("db")
