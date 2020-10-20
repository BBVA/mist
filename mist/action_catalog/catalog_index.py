import os
import json

from mist.catalog import Catalog, catalog_path
from mist.finders import find_commands_folders, find_catalog_metas


def db_insert_command(command_meta: dict,
                      command_versions: dict,
                      catalog_origin: str):

    #
    # Insert catalog indexes
    #
    try:
        cmd_name = command_meta["name"]
    except KeyError:
        raise ValueError("Command INDEX file must has 'name' property")

    try:
        cmd_latest = command_meta["latest"]
    except:
        raise ValueError("Command INDEX file must has 'latest' property")

    try:
        cmd_description = command_meta["description"]
    except:
        raise ValueError("Command INDEX file must has 'description' property")

    if tags := command_meta.get("tags", None):
        cmd_tags = json.dumps([
            x.strip()
            for x in tags.split(",")
        ])
    else:
        cmd_tags = json.dumps([])

    if not catalog_origin:
        catalog_origin = "local"

    command_id = Catalog.add_command(
        cmd_name,
        cmd_description,
        cmd_tags,
        catalog_origin
    )

    #
    # Insert catalog versions
    #
    for version, path in command_versions.items():
        Catalog.add_command_version(
            command_id, version, path
        )



def index_catalog(new_catalog_path: str = None, catalog_origin: str = None):

    new_catalog_path = new_catalog_path or str(catalog_path())

    for (command_path, index_content) in find_commands_folders(new_catalog_path):

        meta_content = {
            x["version"]: command_path
            for x in find_catalog_metas(command_path)
        }

        db_insert_command(index_content, meta_content, catalog_origin)


__all__ = ("index_catalog", )
