from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

from mist.sdk.herlpers import (resolve_list_reference, resolve_dict_reference)
from mist.sdk.exceptions import (MistUndefinedVariableException)

from test.utilTest import *


init_mist()

class CoreResolversTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()
        clean_env_vars()
        clean_mist_params()

    async def test_resolveListReference_raises_MistUndefinedVariableException_if_not_exist(self):

        with self.assertRaisesRegex(MistUndefinedVariableException, "FOO"):
            await resolve_list_reference("FOO", None, [])

    async def test_resolveListReference_raises_TypeError_if_not_a_list(self):
        create_variable("myList", "varValue")

        with self.assertRaisesRegex(TypeError, "myList is a <class 'str'>"):
            await resolve_list_reference("myList", None, get_mistStack())

    async def test_resolveListReference_raises_TypeError_if_not_an_int(self):
        create_variable("myList", ["FOO"])
        tests = [None, "str"]

        for t in tests:
            with self.assertRaisesRegex(TypeError, "list indices must be integers or slices,*"):
                await resolve_list_reference("myList", t, get_mistStack())

    async def test_resolveListReference_returns_None_if_index_not_exist(self):
        create_variable("myList", ["FOO"])

        v = await resolve_list_reference("myList", 1, get_mistStack())

        self.assertIsNone(v)

    async def test_resolveListReference_returns_stored_value(self):
        create_variable("myList", ["value"])

        v = await resolve_list_reference("myList", 0, get_mistStack())

        self.assertEqual("value", v)

    async def test_resolveDictReference_raises_MistUndefinedVariableException_if_not_exist(self):

        with self.assertRaisesRegex(MistUndefinedVariableException, "FOO"):
            await resolve_dict_reference("FOO", None, [])

    async def test_resolveDictReference_raises_TypeError_if_not_a_dict(self):
        create_variable("myDict", "varValue")

        with self.assertRaisesRegex(TypeError, "myDict is a <class 'str'>"):
            await resolve_dict_reference("myDict", None, get_mistStack())

    async def test_resolveDictReference_returns_None_if_key_not_exist(self):
        create_variable("myDict", {"FOO": "BAR"})
        tests = [None, "BAR"]

        for t in tests:
            v = await resolve_dict_reference("myDict", t, get_mistStack())

            self.assertIsNone(v)

    async def test_resolveDictReference_returns_stored_value(self):
        create_variable("myDict", {"key": "val"})

        v = await resolve_dict_reference("myDict", "key", get_mistStack())

        self.assertEqual("val", v)
