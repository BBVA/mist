import os
import tempfile
import re
import xml.etree.ElementTree as ET
import json
from jsonpath_ng.ext import parse
import csv

from mist.sdk import db
from mist.sdk.exceptions import MistException
from mist.sdk.config import config
from mist.sdk.common import watchedInsert

def tmpFileFunction():
    return tempfile.NamedTemporaryFile(delete=False).name

def rangeFunction(begin, end, step):
    return list(range(begin, end, step))

def searchInText(regex: str, text: str):
    found = []

    try:
        found = re.findall(regex, text)
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    finally:
        return found

def searchInXML(xpath: str, text: str):
    found = None

    try:
        root = ET.fromstring(text)
        found = root.findall(xpath)
    except Exception as e:
        print(f" Error in 'BuiltSearchInXML' -> {e}")
    finally:
        return [ {"tag": e.tag, "text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []

def searchInJSON(jsonpath: str, text: str):
    found = None

    try:
        json_data = json.loads(text)
        jsonpath_expression = parse(jsonpath)
        found = jsonpath_expression.find(json_data)
    except Exception as e:
        print(f" Error in 'BuiltSearchInJSON' -> {e}")
    finally:
        return [ e.value for e in found ] if found is not None else []


def CSVput(fileName: str, target: str):
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        try:
            # TODO: ADD CSV HEADER?
            headers = next(reader)

            db.create_table(target, headers)
            for row in reader:
                watchedInsert(target, row)
            return True
        except StopIteration:
            raise MistException(f"Empty file: {fileName}")
            return False
        except Exception as e:
            print(f"Error while creating database: {target}: {e}")
            return False

def CSVdump(source: str, fileName: str):
    with open(fileName, mode='w') as csvFile:
        csvWriter = csv.writer(csvFile,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        headers = db.fetch_table_headers(source)[1:]
        csvWriter.writerow(headers)
        items = db.fetch_table_as_dict(source)
        for row in items:
            row.pop('id', None)
        csvWriter.writerows([
            row.values()
            for row in items
        ])

def readFile(path:str):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    with open(path, 'r') as f:
        fContent = f.read()

    return fContent

def readFileAsLines(path:str):
    if not os.path.isfile(path):
        raise MistException(f"File not found: {path}")

    fContent = []
    with open(path, 'r') as f:
        for l in f:
            fContent.append(l)

    return fContent

class _Functions(dict):

    def __init__(self):
        super(_Functions, self).__init__()
        self["tmpFile"] = {"native": True, "commands": tmpFileFunction}
        self["range"] = {"native": True, "commands": rangeFunction}
        self["searchInText"] = {"native": True, "commands": searchInText}
        self["searchInXML"] = {"native": True, "commands": searchInXML}
        self["searchInJSON"] = {"native": True, "commands": searchInJSON}
        self["CSVput"] = {"native": True, "commands": CSVput}
        self["CSVdump"] = {"native": True, "commands": CSVdump}
        self["readFile"] = {"native": True, "commands": readFile}
        self["readFileAsLines"] = {"native": True, "commands": readFileAsLines}

functions = _Functions()

__all__ = ("functions", )
