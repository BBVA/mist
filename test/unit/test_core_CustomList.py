from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

## Here to remove circular dependency with language_tools.py
import mist.action_run

from mist.lang.classes import (CustomList, ListReference, EnvVariable, ExtParameter, VarReference)
from mist.sdk.exceptions import (MistUndefinedVariableException)
from test.utilTest import *


init_mist()

class CoreCustomListTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()
        clean_env_vars()
        clean_mist_params()

    async def test_CustomList_returns_a_list(self):
        class TestObj:
            def __init__(self, k, v):
                self.key = k
                self.value = v

        create_variable("variable", "varValue")
        create_env_var("envvar", "envarValue")
        create_mist_param("param", "paramValue")
        elements = [ MistObj({"value": 5}),
                     MistObj({"value": "strvalue"}),
                     MistObj({"value": VarReference(None, "variable", None)}),
                     MistObj({"value": EnvVariable(None, "envvar")}),
                     MistObj({"value": ExtParameter(None, "param")})]

        cd = CustomList(None, elements)
        d = await cd.getValue(get_mistStack())

        print(d)
        self.assertEqual([ 5, "strvalue", "varValue", "envarValue", "paramValue" ], d)

    async def test_ListReference_raises_MistUndefinedVariableException_if_not_exist(self):

        dl = ListReference(None, "FOO", "BAR")
        with self.assertRaisesRegex(MistUndefinedVariableException, "FOO"):
            await dl.getValue([])

    async def test_ListReference_raises_TypeError_if_not_a_list(self):
        create_variable("myList", "varValue")

        dl = ListReference(None, "myList", "BAR")
        with self.assertRaisesRegex(TypeError, "myList is a <class 'str'>"):
            await dl.getValue(get_mistStack())

    async def test_ListReference_returns_None_if_index_not_exist(self):
        create_variable("myList", ["FOO"])

        dr = ListReference(None, "myList", 1)
        v = await dr.getValue(get_mistStack())

        self.assertIsNone(v)

    async def test_ListReference_returns_stored_value(self):
        create_variable("myDict", ["value"])

        dl = ListReference(None, "myDict", 0)
        v = await dl.getValue(get_mistStack())

        self.assertEqual("value", v)
