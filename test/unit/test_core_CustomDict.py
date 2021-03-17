from unittest.mock import patch
from unittest import (IsolatedAsyncioTestCase, TestCase, skip)

from mist.lang.classes import (CustomDict, ListDictReference, EnvVariable, ExtParameter, VarReference)
from mist.lang.exceptions import (MistUndefinedVariableException)

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

        self.assertEqual({ "number": 5, "string": "strvalue", "mistVar": "varValue", "mistEnvvar": "envarValue", "mistParam": "paramValue" }, d)

    async def test_ListDictReference_returns_stored_value(self):
        create_variable("myKey", "key")
        create_variable("myDict", {"key": "val"})

        dr = ListDictReference(None, "myDict", MistObj({"value": VarReference(None, "myKey", None)}))
        v = await dr.getValue(get_mistStack())

        self.assertEqual("val", v)
