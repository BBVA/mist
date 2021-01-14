from typing import List
from mist.sdk.db import db
from mist.sdk.watchers import watchers
from mist.sdk.config import config

async def watchedInsert(table: str, stack, values: List[str], *, fields=None):
    if config.debug:
        print(f"-> watchedInsert {table}")
    db.insert(table, values, fields=fields)
    if not fields:
        fields=db.fetch_table_headers(table)[1:]
    item = dict(zip(fields, values))

    for watcher in watchers:
        if watcher["var"] == table:
            stack.append({watcher["name"]: item})
            for c in watcher["commands"]:
                await c.launch(stack)
            stack.pop()
