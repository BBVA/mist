import os
import tempfile
import unittest
from unittest.mock import patch

from mist.sdk.exceptions import MistException
from mist.sdk.functions import (tmpFileFunction, rangeFunction, searchInText,
searchInXML, searchInJSON, CSVput, CSVdump, readFile, readFileAsLines, db)

class NativeFunctionsTest(unittest.TestCase):
    textSearchIn = "aaa bbb aaa ccc bbb ccc aaa bbb"

    def tearDown(self):
        if hasattr(self, 'tmpFile'):
            os.remove(self.tmpFile)
        if hasattr(self, 'readFile'):
            os.remove(self.readFile)
        if hasattr(self, 'CSVPutFile'):
            os.remove(self.CSVPutFile)

    def test_tmpFile(self):
        self.tmpFile = tmpFileFunction()

        self.assertTrue(os.path.isfile(self.tmpFile))

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

    def test_search_text_returns_empty_list_when_not_found(self):
        expected = []

        found = searchInText("d{3}", self.textSearchIn)

        self.assertEqual(expected, found)

    def test_search_text_returns_findings(self):
        expected = ["bbb", "bbb", "bbb"]

        found = searchInText("b{3}", self.textSearchIn)

        self.assertEqual(expected, found)

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

    JSONSearchIn = """
{
    "sons": [
        {
            "name": "BAR",
            "grandsons": [
                {
                    "name": "BAR",
                    "age": 12
                },
                {
                    "name": "FOOBAR",
                    "age": 9
                }
            ]
        },
        {
            "name": "FOO",
            "grandsons": [
                {
                    "name": "BAR",
                    "age": 16
                },
                {
                    "name": "FOOFOO",
                    "age": 14
                }
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

    def test_CSVPut_fails_if_file_doesnt_exists(self):
        with self.assertRaisesRegex(FileNotFoundError, r"\[Errno 2\] No such file or directory: '/imagine'"):
            CSVput("/imagine", "BAR")

    def test_CSVPut_fails_on_empty_file(self):
        self.CSVPutFile = tempfile.NamedTemporaryFile(delete=False).name

        with self.assertRaisesRegex(MistException, f"Empty file: {self.CSVPutFile}"):
            ret = CSVput(self.CSVPutFile, "BAR")
            self.assertFalse(ret)

    @patch.object(db, 'create_table')
    def test_CSVPut_creates_target(self,mock_create_table):
        header = "col01,col02"
        expected = header.split(',')
        table = "myTable"
        self.CSVPutFile = tempfile.NamedTemporaryFile(delete=False).name
        with open(self.CSVPutFile,'w') as f:
            f.write(header)

        ret = CSVput(self.CSVPutFile, table)
        self.assertTrue(ret)
        mock_create_table.assert_called_once_with(table, expected)

##    @patch.object(db, 'create_table')
##    @patch('mist.sdk.common.watchedInsert')
##    def test_CSVPut_creates_target_and_insert_content(self, mock_watchedInsert, mock_create_table):
##        header = "col01,col02"
##        expectedHeader = header.split(',')
##        data = "value01,value02"
##        expectedData = data.split(',')
##        table = "myTable"
##        self.CSVPutFile = tempfile.NamedTemporaryFile(delete=False).name
##        with open(self.CSVPutFile,'w') as f:
##            f.write(header)
##            f.write('\n')
##            f.write(data)
##
##        ret = CSVput(self.CSVPutFile, table)
##        self.assertTrue(ret)
##        mock_create_table.assert_called_once_with(table, expectedHeader)
##        mock_watchedInsert.assert_called_with(table, expectedData, fields=None)
##
##    @unittest.skip("Pending implementation")
##    def test_CSVDump_(self):
##        self.fail("Pending implementation")
##
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

    def test_readFileAsLines_fails_if_file_doesnt_exists(self):
        with self.assertRaisesRegex(MistException, "File not found: /imagine"):
            readFileAsLines("/imagine")

    def test_readFile_returns_empty_string_with_empty_file(self):
        expected = []
        self.readFile = tempfile.NamedTemporaryFile(delete=False).name

        content = readFileAsLines(self.readFile)

        self.assertEqual(expected, content)
