from unittest.mock import patch
from unittest import (IsolatedAsyncioTestCase, TestCase, skip)

from mist.lang.classes import (SetCommand, FunctionCall, ListDictReference)
from mist.lang.exceptions import (MistUndefinedVariableException)

from test.utilTest import *


init_mist()

class CoreSetCommandTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()
        clean_env_vars()
        clean_mist_params()

    async def test_if_a_function_is_given_it_runs(self):
        varName = "var"
        varValue = "val"
        class TestObj:
            def __init__(self, d):
                self.value = d
        f = FunctionCall(None, None, None, None, None, None)
        cmd = SetCommand(None, varName, TestObj(f))

        with patch.object(f, 'run') as mock:
            mock.return_value = varValue
            await cmd.run(get_mistStack())

        mock.assert_called_once()

    @patch('mist.lang.classes.get_id')
    async def test_resolves_id_if_a_function_is_not_given(self, mock_get_id):
        varName = "var"
        varValue = "val"
        mock_get_id.return_value = varValue
        class TestObj:
            def __init__(self, d):
                self.value = d
        v = TestObj(varValue)
        cmd = SetCommand(None, varName, v)

        await cmd.run(get_mistStack())

        mock_get_id.assert_called_once_with(v, get_mistStack())

    @patch('mist.lang.classes.get_id')
    async def test_creates_given_var_with_the_given_value(self, mock_get_id):
        varName = "var"
        varValue = "val"
        mock_get_id.return_value = varValue
        class TestObj:
            def __init__(self, d):
                self.value = d
        v = TestObj(varValue)
        cmd = SetCommand(None, varName, v)

        await cmd.run(get_mistStack())

        self.assertTrue(varName in get_mistStack()[0] and get_mistStack()[0][varName] == varValue)

    async def test_puts_given_value_into_given_dictionary(self):
        dictName = "dict"
        dict = { }
        key = "var"
        value = "val"
        create_variable(dictName, dict)
        class TestObj:
            def __init__(self, d):
                self.value = d

        v = TestObj(value)
        cmd = SetCommand(None, ListDictReference(None, dictName, TestObj(key)), v)

        await cmd.run(get_mistStack())

        self.assertEqual(dict[key], value)

    async def test_sets_given_value_into_given_list_index(self):
        listName = "list"
        value = "Other"
        list = ["One"]
        create_variable(listName, list)
        class TestObj:
            def __init__(self, d):
                self.value = d
        v = TestObj(value)
        cmd = SetCommand(None, ListDictReference(None, listName, TestObj(0)), v)

        await cmd.run(get_mistStack())

        self.assertEqual(list[0], value)
