from unittest.mock import patch
from unittest import (IsolatedAsyncioTestCase, TestCase, skip)

## Here to remove circular dependency with language_tools.py
import mist.action_run

from mist.lang.classes import (CustomDict, DictReference, EnvVariable, ExtParameter, VarReference)
from mist.sdk.exceptions import (MistUndefinedVariableException)

from test.utilTest import *


init_mist()

class CoreCustomDictTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()
        clean_env_vars()
        clean_mist_params()

    async def test_CustomDict_returns_a_dictionary(self):
        class TestObj:
            def __init__(self, k, v):
                self.key = k
                self.value = v

        create_variable("variable", "varValue")
        create_env_var("envvar", "envarValue")
        create_mist_param("param", "paramValue")
        entries = [ TestObj("number", MistObj({"value": 5})),
                    TestObj("string", MistObj({"value": "strvalue"})),
                    TestObj("mistVar", MistObj({"value": VarReference(None, "variable", None)})),
                    TestObj("mistEnvvar", MistObj({"value": EnvVariable(None, "envvar")})),
                    TestObj("mistParam", MistObj({"value": ExtParameter(None, "param")}))]

        cd = CustomDict(None, entries)
        d = await cd.getValue(get_mistStack())

        print(d)
        self.assertEqual({ "number": 5, "string": "strvalue", "mistVar": "varValue", "mistEnvvar": "envarValue", "mistParam": "paramValue" }, d)

    async def test_DictReference_raises_MistUndefinedVariableException_if_not_exist(self):

        dr = DictReference(None, "FOO", "BAR")
        with self.assertRaisesRegex(MistUndefinedVariableException, "FOO"):
            await dr.getValue([])

    async def test_DictReference_raises_TypeError_if_not_a_dict(self):
        create_variable("myDict", "varValue")

        dr = DictReference(None, "myDict", "BAR")
        with self.assertRaisesRegex(TypeError, "myDict is a <class 'str'>"):
            await dr.getValue(get_mistStack())

    async def test_DictReference_returns_None_if_key_not_exist(self):
        create_variable("myDict", {"FOO": "BAR"})

        dr = DictReference(None, "myDict", "BAR")
        v = await dr.getValue(get_mistStack())

        self.assertIsNone(v)

    async def test_DictReference_returns_stored_value(self):
        create_variable("myDict", {"key": "val"})

        dr = DictReference(None, "myDict", "key")
        v = await dr.getValue(get_mistStack())

        self.assertEqual("val", v)
