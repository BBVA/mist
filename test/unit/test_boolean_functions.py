from unittest import (IsolatedAsyncioTestCase, TestCase, skip)
from unittest.mock import patch

import sqlite3

from mist.lang.function import (functions, boolNot, boolAnd, boolOr)

class BooleanFunctionsTest(TestCase):

######
###### Check for exported functions
######
    def test_all_functions_are_exported(self):
        ef = [("NOT", boolNot), ("AND", boolAnd), ("OR", boolOr)]

        for i in ef:
            self.assertTrue(i[0] in functions and functions[i[0]]["commands"] == i[1] and functions[i[0]]["native"], f"{i} not exported")
            if len(i) > 2:
                self.assertEqual(i[2], functions[i[0]]["async"])

######
###### Tests for boolNot
######
    def test_boolNot_returns_negated_param(self):
        tests = [True, False]

        for t in tests:
            r = boolNot(t)

            self.assertEqual(not t, r)

######
###### Tests for boolAnd
######
    def test_boolAnd_returns_and_of_params(self):
        tests = [{'args': [False, False, False], 'ret': False}, {'args': [True, False, False], 'ret': False}, {'args': [True, True, False], 'ret': False}, {'args': [True, True, True], 'ret': True}]

        for t in tests:
            r = boolAnd(*t['args'])

            self.assertEqual(t['ret'], r)

######
###### Tests for boolOr
######
    def test_boolOr_returns_or_of_params(self):
        tests = [{'args': [False, False, False], 'ret': False}, {'args': [True, False, False], 'ret': True}, {'args': [True, True, False], 'ret': True}, {'args': [True, True, True], 'ret': True}]

        for t in tests:
            r = boolOr(*t['args'])

            self.assertEqual(t['ret'], r)
