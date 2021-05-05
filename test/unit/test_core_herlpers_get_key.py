import unittest

from unittest.mock import patch

from mist.lang.herlpers import get_key, NamedArg

from test.utilTest import *

from mist.lang.classes import VarReference


class Get_key_Test(unittest.IsolatedAsyncioTestCase):

    async def test_returns_string_content_when_given_a_string(self):
        result = "value"

        ret = await get_key("'" + result + "'", [])

        self.assertEqual(result, ret)

    async def test_returns_parameter_value_when_given_a_mist_parameter(self):
        var_name = "myVar"
        var_value = "FOO"
        init_mist()
        create_mist_param(var_name, var_value)

        ret = await get_key("%" + var_name, [])

        self.assertEqual(var_value, ret)

    async def test_returns_envvar_value_when_given_a_env_variable(self):
        var_name = "myVar"
        var_value = "FOO"
        init_mist()
        create_env_var(var_name, var_value)

        ret = await get_key("$" + var_name, [])

        self.assertEqual(var_value, ret)

    #@unittest.skip("WIP")
    @patch('mist.lang.herlpers.function_runner')
    async def test_returns_function_return_value_when_given_a_function_without_args(self, mock_function_runner):
        result = "function_return_value"
        mock_function_runner.return_value = result

        ret = await get_key("myFunc()", [])

        self.assertEqual(result, ret)
        mock_function_runner.assert_called_once_with(VarReference(parent=None, id='myFunc', childs=[]), [], None, None, [])

    @patch('mist.lang.herlpers.function_runner')
    async def test_returns_function_return_value_when_given_a_function_with_args(self, mock_function_runner):
        result = "function_return_value"
        mock_function_runner.return_value = result

        ret = await get_key("myFunc(one, two, three)", [])

        self.assertEqual(result, ret)
        mock_function_runner.assert_called_once_with(VarReference(parent=None, id='myFunc', childs=[]), [], None, None, ["one", "two", "three"])

    @patch('mist.lang.herlpers.function_runner')
    async def test_returns_function_return_value_when_given_a_function_with_named_args(self, mock_function_runner):

        result = "function_return_value"
        mock_function_runner.return_value = result

        ret = await get_key("myFunc(one=1, two=2, three=3)", [])

        self.assertEqual(result, ret)
        mock_function_runner.assert_called_once_with(VarReference(parent=None, id='myFunc', childs=[]), [], None, None, None, [NamedArg("one", "1"), NamedArg("two", "2"), NamedArg("three", "3")])

    @patch('mist.lang.herlpers.get_var')
    @patch('mist.lang.herlpers.getChildFromVar')
    async def test_returns_var_value_when_given_a_composed_variable_name(self, mock_getChildFromVar, mock_get_var):
        result = "part_value"
        result1 = "whole_value"
        mock_get_var.return_value = result
        mock_getChildFromVar.return_value = result1

        ret = await get_key("part.child", [])

        self.assertEqual(result1, ret)
        mock_get_var.assert_called_once_with("part", [])
        mock_getChildFromVar.assert_called_once_with(result, ["child"])

    async def test_returns_var_value_when_given_a_variable_name(self):
        var_name = "myVar"
        var_value = "FOO"
        init_mist()
        create_variable(var_name, var_value)

        ret = await get_key(var_name, get_mistStack())

        self.assertEqual(var_value, ret)

    async def test_returns_list_component_when_given_a_list_reference(self):
        var_name = "myList"
        var_value = ["a", "b"]
        init_mist()
        create_variable(var_name, var_value)

        ret = await get_key(var_name + "[0]", get_mistStack())

        self.assertEqual("a", ret)

    async def test_returns_dictionary_component_when_given_a_dictionary_reference(self):
        var_name = "myDict"
        var_value = {"a": 1, "b": 2}
        init_mist()
        create_variable(var_name, var_value)

        ret = await get_key(var_name + '["b"]', get_mistStack())

        self.assertEqual(2, ret)
