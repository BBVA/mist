import unittest

from unittest.mock import patch, call

from mist.lang.herlpers import get_id, ValueContainer

from test.utilTest import *


class Get_id_Test(unittest.IsolatedAsyncioTestCase):

    async def test_returns_None_when_given_None(self):

        ret = await get_id(None, [])

        self.assertIsNone(ret)

    @patch('mist.lang.herlpers.get_var')
    async def test_returns_True_when_given_True_or_Success_string(self, mock_get_var):
        mock_get_var.return_value = True
        param = [ "True", "Success"]

        for p in param:
            ret = await get_id(p, [])

            self.assertTrue(ret)
            mock_get_var.assert_called_once_with(p, [])

            mock_get_var.reset_mock()

    @patch('mist.lang.herlpers.get_var')
    async def test_returns_False_when_given_False_or_Error_string(self, mock_get_var):
        mock_get_var.return_value = False
        param = ["False", "Error"]

        for p in param:
            ret = await get_id(p, [])

            self.assertFalse(ret)
            mock_get_var.assert_called_once_with(p, [])
            mock_get_var.reset_mock()

    @patch('mist.lang.herlpers.get_key')
    async def test_returns_Formatted_string_when_given_parameterized_string(self, mock_get_key):

        async def get_key_SE(p, stack):
            p = p.strip()
            if p[0] == "'" and p[-1] == "'":
                return p[1:-1]
            if p[0] == '%' or p[0] == '$':
                return p[1:]

        mock_get_key.side_effect = get_key_SE
        param = "Test formatted {%param}, {$env_var}, {'test'}"
        result = "Test formatted param, env_var, test"

        ret = await get_id(MistObj({ 'value': param}), [])

        self.assertEqual(result, ret)
        mock_get_key.assert_has_calls([call("%param", []), call("$env_var", []), call("'test'", [])])

    async def test_returns_integer_when_given_integer(self):
        val = 45

        ret = await get_id(MistObj({ 'value': val}), [])

        self.assertEqual(ret, val)

    async def test_returns_value_from_ValueContainer_when_given_a_ValueContainer(self):
        result = 'FOO'
        class myTestClass(ValueContainer):
            def __init__(self,d):
                self.data = d

            async def getValue(self, stack):
                return self.data

        ret = await get_id(MistObj({ 'value':myTestClass(result) }), [])

        self.assertEqual(result, ret)
