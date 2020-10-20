import os

from typing import Iterator, Tuple

from mist.files import skip_dir
from mist.validators import validate_index_file, validate_command_meta


def find_commands_folders(path: str) -> Iterator[Tuple[str, dict]]:
    """
    Find in a path for commands folders.

    Each time it found a command folder, returns folder and 'INDEX' file
    content

    :return: Iterator(COMMAND FOLDER: str, INDEX CONTENT: dict)

    """

    for root, dirs, files in os.walk(path, topdown=True, followlinks=True):

        if skip_dir(root):
            continue

        if "INDEX" not in files:
            continue

        # Finding INDEX command package
        index_file = os.path.join(root, "INDEX")

        if not (index_content := validate_index_file(index_file)):
            continue

        yield root, index_content


def find_catalog_metas(base_command_path: str) -> Iterator[Tuple[str, dict]]:
    """
    this functions find all command versions and return a dict as format

    Iterate format:

    (path: str, meta_content:dict)
    """
    found_metas = {}

    for root, dirs, files in os.walk(base_command_path,
                                     topdown=True,
                                     followlinks=True):

        if skip_dir(root):
            continue

        if "META" not in files:
            continue

        # Finding INDEX command package
        meta_file = os.path.join(root, "META")

        if not (meta_content := validate_command_meta(meta_file)):
            continue

        yield root, meta_content

    return found_metas


__all__ = ("find_commands_folders", "find_catalog_metas")
