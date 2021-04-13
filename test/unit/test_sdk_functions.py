import os
import tempfile
from unittest import (IsolatedAsyncioTestCase, TestCase, skip)
from unittest.mock import patch

from mist.lang.exceptions import MistException
from mist.lang.function import (functions, tmpFileFunction, fileWriteLine, rangeFunction,
                                searchInText, searchInXML, searchInJSON,
                                readFile, readFileAsLines, objectLen, listMap, listReduce)

class NativeFunctionsTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        ### For tmpFileFunction tests
        if hasattr(self, 'tmpFile'):
            os.remove(self.tmpFile)
        ### For readFile tests
        if hasattr(self, 'readFile'):
            os.remove(self.readFile)
        ### For fileWriteLine tests
        if hasattr(self, 'fileWriteLine'):
            os.remove(self.fileWriteLine)

######
###### Check for exported functions
######
    def test_all_functions_are_exported(self):
        ef = [("tmpFile", tmpFileFunction), ("writeLine", fileWriteLine), ("range", rangeFunction),
              ("searchInText", searchInText), ("searchInXML", searchInXML), ("searchInJSON", searchInJSON),
              ("readFile", readFile), ("readFileAsLines", readFileAsLines),
              ("len", objectLen), ("map", listMap), ("reduce", listReduce), ]

        for i in ef:
            self.assertTrue(i[0] in functions and functions[i[0]]["commands"] == i[1] and functions[i[0]]["native"], f"{i} not exported")
            if len(i) > 2:
                self.assertEqual(i[2], functions[i[0]]["async"])

######
###### Tests for tmpFileFunction
######
    def test_tmpFile(self):
        self.tmpFile = tmpFileFunction()

        self.assertTrue(os.path.isfile(self.tmpFile))

######
###### Tests for fileWriteLine
######
    def test_fileWriteLine_creates_file_and_writes_line(self):
        expected = "FOO BAR BAZZ"
        self.fileWriteLine = tempfile.NamedTemporaryFile(delete=False).name

        fileWriteLine(self.fileWriteLine, expected)

        with open(self.fileWriteLine, 'r') as f:
            r = f.read()

        self.assertEqual(expected + '\n', r)

    def test_fileWriteLine_appends_to_file(self):
        expected = "FOO BAR BAZZ"
        self.fileWriteLine = tempfile.NamedTemporaryFile(delete=False).name

        fileWriteLine(self.fileWriteLine, expected)
        fileWriteLine(self.fileWriteLine, expected)
        fileWriteLine(self.fileWriteLine, expected)

        with open(self.fileWriteLine, 'r') as f:
            r = f.read()

        self.assertEqual((expected + '\n')* 3, r)

######
###### Tests for rangeFunction
######
    def test_range_up_by_one(self):
        expected = [0, 1, 2, 3, 4]
        got = rangeFunction(0,5,1)

        self.assertEqual(expected, got)

    def test_range_down_by_one(self):
        expected = [5, 4, 3, 2, 1]
        got = rangeFunction(5,0,-1)

        self.assertEqual(expected, got)

    def test_range_up_by_three(self):
        expected = [0, 3, 6]
        got = rangeFunction(0,9,3)

        self.assertEqual(expected, got)

    def test_range_down_by_three(self):
        expected = [9, 6, 3]
        got = rangeFunction(9,0,-3)

        self.assertEqual(expected, got)

######
###### Tests for searchInText
######
    textSearchIn = "aaa bbb aaa ccc bbb ccc aaa bbb"

    def test_search_text_returns_empty_list_when_not_found(self):
        expected = []

        found = searchInText("d{3}", self.textSearchIn)

        self.assertEqual(expected, found)

    def test_search_text_returns_findings(self):
        expected = ["bbb", "bbb", "bbb"]

        found = searchInText("b{3}", self.textSearchIn)

        self.assertEqual(expected, found)

######
###### Tests for searchInXML
######
    XMLSearchIn = """<?xml version="1.0" ?>
<root>
    <son name="BAR">
        <grandson name="BAR" age="12" />
        <grandson name="FOOBAR" age="9" />
    </son>
    <son name="FOO">
        <grandson name="BAR" age="16" />
        <grandson name="FOOFOO" age="14" />
    </son>
</root>
"""

    def test_search_xml_returns_empty_list_when_not_found(self):
        expected = []

        found = searchInXML(".//grandson[@name='BARFOO']", self.XMLSearchIn)

        self.assertEqual(expected, found)

    def test_search_xml_returns_findings(self):
        expected = [
                    {'tag': 'grandson', 'attributes': {'name': 'BAR', 'age': '12'}, 'text': None},
                    {'tag': 'grandson', 'attributes': {'name': 'BAR', 'age': '16'}, 'text': None}
                   ]

        found = searchInXML(".//grandson[@name='BAR']", self.XMLSearchIn)

        self.assertEqual(expected, found)

######
###### Tests for searchInJSON
######
    JSONSearchIn = """
{
    "sons": [
        {
            "name": "BAR",
            "grandsons": [
                { "name": "BAR", "age": 12 },
                { "name": "FOOBAR", "age": 9 }
            ]
        },
        {
            "name": "FOO",
            "grandsons": [
                { "name": "BAR", "age": 16 },
                { "name": "FOOFOO", "age": 14 }
            ]
        }
    ]
}
"""
    def test_search_JSON_returns_empty_list_when_not_found(self):
        expected = []

        found = searchInJSON("$..grandsons[?(@.name=='FOO')]", self.JSONSearchIn)

        self.assertEqual(expected, found)


    def test_search_JSON_returns_findings(self):
        expected = [
                      { 'name': 'BAR', 'age': 12 },
                      { 'name': 'BAR', 'age': 16 }
                    ]

        found = searchInJSON("$..grandsons[?(@.name=='BAR')]", self.JSONSearchIn)

        self.assertEqual(expected, found)

######
###### Tests for readFile
######
    def test_readFile_fails_if_file_doesnt_exists(self):
        with self.assertRaisesRegex(MistException, "File not found: /imagine"):
            readFile("/imagine")

    def test_readFile_returns_empty_string_with_empty_file(self):
        expected = ""
        self.readFile = tempfile.NamedTemporaryFile(delete=False).name

        content = readFile(self.readFile)

        self.assertEqual(expected, content)

    def test_readFile_returns_file_content(self):
        expected = "FOO BAR, FOO BAR, FOO BAR, BAR FOO\n, BAR FOO, BAR FOO, BAR FOO, FOO BAR\nFOO, FOO FOO, FOO FOO FOO\n"
        self.readFile = tempfile.NamedTemporaryFile(delete=False).name
        with open(self.readFile,'w') as f:
            f.write(expected)

        content = readFile(self.readFile)

        self.assertEqual(expected, content)

######
###### Tests for readFileAsLines
######
    def test_readFileAsLines_fails_if_file_doesnt_exists(self):
        with self.assertRaisesRegex(MistException, "File not found: /imagine"):
            readFileAsLines("/imagine")

    def test_readFile_returns_empty_string_with_empty_file(self):
        expected = []
        self.readFile = tempfile.NamedTemporaryFile(delete=False).name

        content = readFileAsLines(self.readFile)

        self.assertEqual(expected, content)

######
###### Tests for objectLen
######
    def test_objectLen_returns_the_correct_list_length(self):
        self.assertEqual(0, objectLen([]))
        self.assertEqual(3, objectLen(["BAR", "FOO", "BAZ"]))

    def test_objectLen_returns_the_correct_str_length(self):
        self.assertEqual(0, objectLen(""))
        self.assertEqual(3, objectLen("BAR"))

######
###### Tests for listMap
######
    def test_listMap_fails_if_None_received(self):
        with self.assertRaisesRegex(MistException, "No list received"):
            listMap(None, None)

    def test_listMap_fails_if_not_a_list(self):
        with self.assertRaisesRegex(MistException, "Not a list"):
            listMap("list", None)

    def test_listMap_fails_if_not_a_function(self):
        with self.assertRaisesRegex(MistException, "Not a function"):
            listMap([], None)
        with self.assertRaisesRegex(MistException, "Not a function"):
            listMap([], "BAR")

    def test_listMap_maps_as_a_champion(self):
        l = [2, 3, 4]

        r = listMap(l, lambda x: x * 2)

        self.assertTrue(l is r)
        self.assertEqual(4, r[0])
        self.assertEqual(6, r[1])
        self.assertEqual(8, r[2])

######
###### Tests for listReduce
######
    def test_listReduce_fails_if_None_received(self):
        with self.assertRaisesRegex(MistException, "No list received"):
            listReduce(None, None)

    def test_listReduce_fails_if_not_a_list(self):
        with self.assertRaisesRegex(MistException, "Not a list"):
            listReduce("list", None)

    def test_listReduce_fails_if_not_a_function(self):
        with self.assertRaisesRegex(MistException, "Not a function"):
            listReduce([], None)
        with self.assertRaisesRegex(MistException, "Not a function"):
            listReduce([], "BAR")

    def test_listReduce_reduces_as_a_champion(self):
        l = [2, 3, 4]
        def sum(x, y):
            if x is None:
                x = 0
            return x + y

        r = listReduce(l, sum)

        self.assertEqual(9, r)
