import tempfile
import re
import xml.etree.ElementTree as ET
import json
from jsonpath_ng import parse
import csv

from mist.sdk import db
from mist.sdk.config import config
from mist.sdk.common import watchedInsert

def tmpFileFunction():
    return tempfile.NamedTemporaryFile(delete=False).name

def rangeFunction(begin, end, step):
    return list(range(begin, end, step))

def searchInText(regex: str, text: str):
    try:
        if re.findall(regex, text):
            return True
    except Exception as e:
        print(f" Error in 'BuiltSearchInText' -> {e}")
    return False

def searchInXML(xpath: str, text: str):
    try:
        root = ET.fromstring(text)
        found = root.findall(xpath)
    except Exception as e:
        print(f" Error in 'BuiltSearchInXML' -> {e}")
        return False
    return [ {"text": e.text, "attributes": e.attrib } for e in found ] if found is not None else []

def searchInJSON(jsonpath: str, text: str):
    try:
        json_data = json.loads(text)
        jsonpath_expression = parse(jsonpath)
        found = jsonpath_expression.find(json_data)
    except Exception as e:
        print(f" Error in 'BuiltSearchInJSON' -> {e}")
        return False
    return [ e.value for e in found ] if found is not None else []


def CSVput(fileName: str, target: str):
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # TODO: ADD CSV HEADER?
        headers = next(reader)
        try:
            db.create_table(target, headers)
            for row in reader:
                watchedInsert(target, row)
            return True
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

functions = _Functions()

__all__ = ("functions", )
