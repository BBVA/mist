from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

from mist.lang.classes import (CustomList, ListDictReference, EnvVariable, ExtParameter, VarReference)
from mist.lang.exceptions import (MistUndefinedVariableException)

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

        self.assertEqual([ 5, "strvalue", "varValue", "envarValue", "paramValue" ], d)

    async def test_ListDictReference_returns_stored_value(self):
        create_variable("myIndex", 0)
        create_variable("myList", ["value"])

        dl = ListDictReference(None, "myList", MistObj({"value": VarReference(None, "myIndex", None)}))
        v = await dl.getValue(get_mistStack())

        self.assertEqual("value", v)
