"""
This file builds the documentation for APICheck
"""
import os
import re
import json
import shutil
import hashlib
import configparser

HERE = os.path.abspath(os.path.dirname(__file__))

DOC_PATH = os.path.join(HERE, "docs", "source")
CATALOG = os.path.join(HERE, "mist", "catalog")

def main():

    #
    # Check if destination catalog folder exits
    #
    doc_catalog_path = os.path.join(DOC_PATH, "catalog")
    if not os.path.exists(doc_catalog_path):
        os.mkdir(doc_catalog_path)

    commands_in_catalog = []

    #
    # Copy catalog README files
    #
    for d in os.listdir(CATALOG):

        if d.startswith("."):
            continue

        command_name = d.split(os.path.sep)[-1]

        # Get README.rst file
        readme_path = os.path.join(CATALOG, d, "README.rst")

        # Ensure docs/ has a folder with tool name
        doc_path_folder = os.path.join(DOC_PATH, "catalog", command_name)
        if not os.path.exists(doc_path_folder):
            os.mkdir(doc_path_folder)

        # Copy readme
        shutil.copy(readme_path, os.path.join(doc_path_folder, "README.rst"))

        commands_in_catalog.append(command_name)

    # Update index.rst
    with open(os.path.join(DOC_PATH, "index.rst"), "a+") as f:
        # catalog
        catalog_commands = '\n'.join(
            f'   catalog/{command}/README.rst' for command in commands_in_catalog
        )
        catalog = f'''        
.. toctree::
   :caption: Catalog
   :name: mastertoc
   :maxdepth: 2

{catalog_commands}
        '''
        f.write(catalog)


if __name__ == '__main__':
    main()
