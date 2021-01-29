import unittest
from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from mist.sdk.exceptions import MistUndefinedVariableException, MistException

#from mist.sdk.herlpers import get_id, get_param, get_key, watchedInsert, command_runner, function_runner

import mist.sdk.herlpers
from mist.lang.classes import SaveListCommand

from test.utilTest import *

# Alternativas de mockeo
### 1. Monkeypatch
#def .....
#mist.sdk.helpers.watchedInsert =

### 2. unittest.mock

init_mist({ "debug": True })

stack = [{"MistBaseNamespace": True}]

class SaveCommandTest(IsolatedAsyncioTestCase):

    def tearDown(self):
        clean_variables()

    async def test_error_when_no_list_found(self):
        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=None,
                    sources=None,
                    target="MyTable",
                    params=None)
        with self.assertRaisesRegex(MistUndefinedVariableException, "myList"):
            await cmd.run(get_mistStack())

    async def test_error_when_list_is_not_of_type_list(self):
        create_variable("myList", "BAR")

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=None,
                    sources=None,
                    target="MyTable",
                    params=None)
        with self.assertRaisesRegex(MistException, "myList is not a list"):
            await cmd.run(get_mistStack())


    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_no_modifiers(self, mock_watchedInsert):
        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=None,
                    sources=None,
                    target="MyTable",
                    params=None)
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value01", "value02"], fields=None)

    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_selectors(self, mock_watchedInsert):

        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=["key02"],
                    sources=None,
                    target="MyTable",
                    params=None)
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value02"], fields=None)

    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_columns(self, mock_watchedInsert):

        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=None,
                    sources=None,
                    target="MyTable",
                    params=["Col1", "Col1"])
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value01", "value02"], fields=["Col1", "Col1"])

    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_columns_and_selectors(self, mock_watchedInsert):

        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=["key02", "key01"],
                    sources=None,
                    target="MyTable",
                    params=["Col2", "Col1"])
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value02", "value01"], fields=["Col2", "Col1"])

    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_selectors_and_values(self, mock_watchedInsert):

        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=["key02"],
                    sources=[MistObj({'value': "fix01"})],
                    target="MyTable",
                    params=None)
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value02", "fix01"], fields=None)

    @patch('mist.lang.classes.watchedInsert')
    async def test_put_with_selectors_columns_and_values(self, mock_watchedInsert):

        create_variable("myList", [{"key01": "value01", "key02": "value02"}])

        cmd = SaveListCommand(
                    parent=None,
                    list="myList",
                    selectors=["key02"],
                    sources=[MistObj({'value': "fix01"})],
                    target="MyTable",
                    params=["Col2", "Col1"])
        await cmd.run(get_mistStack())

        mock_watchedInsert.assert_called_once()
        mock_watchedInsert.assert_called_with("MyTable", [{'MistBaseNamespace': True}, {'myList': [{'key01': 'value01', 'key02': 'value02'}]}], ["value02", "fix01"], fields=["Col2", "Col1"])
