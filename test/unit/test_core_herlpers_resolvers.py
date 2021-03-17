from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

from mist.lang.herlpers import (resolve_list_dict_reference)
from mist.lang.exceptions import (MistUndefinedVariableException)

from test.utilTest import *


init_mist()

class CoreResolversTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()
        clean_env_vars()
        clean_mist_params()

    @patch("mist.lang.herlpers.get_var")
    async def test_resolveListDictReference_raises_MistUndefinedVariableException_if_not_exist(self, mock_get_var):
        varName = "FOO"
        mock_get_var.side_effect = MistUndefinedVariableException(varName)

        with self.assertRaisesRegex(MistUndefinedVariableException, varName):
            await resolve_list_dict_reference(varName, None, [])

    async def test_resolveListDictReference_raises_TypeError_if_not_a_list_neither_a_dict(self):
        varName = "myList"
        create_variable(varName, "varValue")

        with self.assertRaisesRegex(TypeError, f"{varName} is not a list neither a dict"):
            await resolve_list_dict_reference(varName, None, get_mistStack())

    @patch("mist.lang.herlpers.get_id")
    async def test_resolveListDictReference_doesnt_resolve_member_if_int(self, mock_get_id):
        varName = "myList"
        intVal = 0
        create_variable(varName, ["BAR"])

        await resolve_list_dict_reference(varName, intVal, get_mistStack())

        mock_get_id.assert_not_called()

    @patch("mist.lang.herlpers.get_id")
    async def test_resolveListDictReference_doesnt_resolve_member_if_quoted_string(self, mock_get_id):
        varName = "myDict"
        quotStrVal = '"FOO"'
        create_variable(varName, {"FOO": "BAR"})

        await resolve_list_dict_reference(varName, quotStrVal, get_mistStack())

        mock_get_id.assert_not_called()

    @patch("mist.lang.herlpers.get_id")
    async def test_resolveListDictReference_resolves_member(self, mock_get_id):
        varName = "myList"
        expected = "FOO"
        create_variable(varName, ["BAR"])
        mock_get_id.return_value = 0

        await resolve_list_dict_reference(varName, expected, get_mistStack())

        mock_get_id.assert_called_once_with(expected, get_mistStack())

    async def test_resolveListDictReference_raises_TypeError_when_accessing_list_with_non_int(self):
        create_variable("myIndex", "FOO")
        create_variable("myList", ["FOO"])

        with self.assertRaisesRegex(TypeError, "list indices must be integers or slices,*"):
            await resolve_list_dict_reference("myList", "myIndex", get_mistStack())

    async def test_resolveListDictReference_returns_None_if_index_not_exist_in_list(self):
        create_variable("myIndex", 1)
        create_variable("myList", ["FOO"])

        v = await resolve_list_dict_reference("myList", "myIndex", get_mistStack())

        self.assertIsNone(v)

    async def test_resolveListDictReference_returns_None_if_key_not_exist_in_dict(self):
        create_variable("myKey", "key")
        create_variable("myDict", {"FOO": "BAR"})

        v = await resolve_list_dict_reference("myDict", "myKey", get_mistStack())

        self.assertIsNone(v)

    async def test_resolveListDictReference_returns_stored_value_in_list(self):
        create_variable("myIndex", 0)
        create_variable("myList", ["value"])

        v = await resolve_list_dict_reference("myList", "myIndex", get_mistStack())

        self.assertEqual("value", v)

    async def test_resolveListDictReference_returns_stored_value_in_dict(self):
        create_variable("myKey", "key")
        create_variable("myDict", {"key": "val"})

        v = await resolve_list_dict_reference("myDict", "myKey", get_mistStack())

        self.assertEqual("val", v)
