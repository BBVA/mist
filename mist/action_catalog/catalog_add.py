import os
import shutil
import argparse

from mist.net_utils import file_uri_to_path, download, git_clone
from mist.sdk import config, MistException

from mist.catalog import catalog_path

from .catalog_index import index_catalog


# -------------------------------------------------------------------------
# Helpers for catalog add
# -------------------------------------------------------------------------
def catalog_add(parsed_args: argparse.Namespace or str):

    if type(parsed_args) is str:
        catalog_uri = parsed_args
    else:
        catalog_uri = config.CATALOG

    mist_catalog = catalog_path()

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
            dst = str(file_uri_to_path(catalog_uri)).replace(".git", "")[1:]

            catalog_dst = mist_catalog.joinpath(dst)

            if not catalog_dst.exists():
                catalog_dst.mkdir(parents=True)

            if not config.get("quiet", False):
                print("[*] Downloading core catalog...", end='', flush=True)

            try:
                git_clone(catalog_uri, str(catalog_dst))
            except MistException:
                pass

            if not config.get("quiet", False):
                print("Done", flush=True)

        # Check if is a remote web
        else:
            catalog_dst = str(file_uri_to_path(catalog_uri)).replace(".git", "")[1:]

            try:
                download(catalog_uri, catalog_dst)
            except Exception as e:
                MistException(
                    f"Error while try to download catalog: '{catalog_uri}'"
                )

    # Checks if is path existing path
    elif os.path.exists(catalog_uri):

        # TODO: check catalog_dst
        shutil.copy(catalog_uri, mist_catalog)

    else:
        raise MistException(
            "Can't find catalog. If you are trying to add a remote catalog"
            "it must starts as 'http://' or 'https://'"
        )

    #
    # Index catalog
    #
    index_catalog(catalog_dst, catalog_uri)



__all__ = ("catalog_add", )
