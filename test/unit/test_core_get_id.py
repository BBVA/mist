import unittest
from unittest.mock import patch, call

from mist.sdk.exceptions import MistException

from mist.sdk.herlpers import get_id

from test.utilTest import *


class Get_id_Test(unittest.TestCase):

    def test_returns_None_when_given_None(self):

        ret = get_id(None)

        self.assertIsNone(ret)

    @patch('mist.sdk.herlpers.get_var')
    def test_returns_True_when_given_True_or_Success_string(self, mock_get_var):
        mock_get_var.return_value = True
        param = [ "True", "Success"]

        for p in param:
            ret = get_id(p)

            self.assertTrue(ret)
            mock_get_var.assert_called_once_with(p)

            mock_get_var.reset_mock()

    @patch('mist.sdk.herlpers.get_var')
    def test_returns_False_when_given_False_or_Error_string(self, mock_get_var):
        mock_get_var.return_value = False
        param = ["False", "Error"]

        for p in param:
            ret = get_id(p)

            self.assertFalse(ret)
            mock_get_var.assert_called_once_with(p)
            mock_get_var.reset_mock()

    @patch('mist.sdk.herlpers.get_key')
    def test_returns_Formatted_string_when_given_parameterized_string(self, mock_get_key):

        def get_key_SE(p):
            p=p.strip()
            if p[0] == "'" and p[-1] == "'":
                return p[1:-1]
            if p[0] == '%' or p[0] == '$':
                return p[1:]

        mock_get_key.side_effect = get_key_SE
        param = "Test formatted {%param}, {$env_var}, {'test'}"
        result = "Test formatted param, env_var, test"

        ret = get_id(MistObj({ 'value': param}))

        self.assertEqual(result, ret)
        mock_get_key.assert_has_calls([call("%param"), call("$env_var"), call("'test'")])

    def test_returns_integer_when_given_integer(self):
        val = 45

        ret = get_id(MistObj({ 'value': val}))

        self.assertEqual(ret, val)
