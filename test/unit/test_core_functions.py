from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

from mist.sdk.function import (functions, corePrint, coreAbort, corePut,
                                corePutData, coreSend, parseInt, toString)
from mist.sdk.exceptions import (MistException, MistAbortException, MistUndefinedVariableException)


class CoreFunctionsTest(IsolatedAsyncioTestCase):

######
###### Check for exported functions
######
    def test_all_functions_are_exported(self):
        ef = [("print", corePrint), ("abort", coreAbort), ("put", corePut, True), ("putData", corePutData, True), ("send", coreSend, True)]

        for i in ef:
            self.assertTrue(i[0] in functions and functions[i[0]]["commands"] == i[1] and functions[i[0]]["native"], f"{i} not exported")
            if len(i) > 2:
                self.assertEqual(i[2], functions[i[0]]["async"])

######
###### corePrint
######
    @patch('mist.sdk.function.print')
    @patch('mist.sdk.function.helpers.get_id')
    def test_CorePrint_call_python_print_with_all_its_params(self, mock_getId, mock_print):
        stack = []
        mock_getId.side_effect = lambda id, stack: id

        corePrint("one", "two", "three", "four", "five", stack=stack, commands=None)

        mock_print.assert_called_with("one", "two", "three", "four", "five")

######
###### coreAbort
######
    def test_coreAbort_raises_exception_when_no_reason_given(self):
        expected = "Abort reached"

        with self.assertRaisesRegex(MistAbortException, expected):
            coreAbort(stack=[], commands=None)
            coreAbort(None, stack=[], commands=None)
            coreAbort("", stack=[], commands=None)

    def test_coreAbort_raises_exception_with_reason_given(self):
        expected = "Abort forced"

        with self.assertRaisesRegex(MistAbortException, expected):
            coreAbort(expected, stack=[], commands=None)

######
###### corePut
######
    async def test_corePut_raises_MistException_when_no_table_given(self):
        expected = "A table is needed"

        with self.assertRaisesRegex(MistException, expected):
            await corePut(None, stack=[], commands=None)
            await corePut(None, None, stack=[], commands=None)
            await corePut("", None, stack=[], commands=None)

    async def test_corePut_raises_MistException_when_no_data_given(self):
        expected = "Data items to store needed"

        with self.assertRaisesRegex(MistException, expected):
            await corePut("FOO", stack=[], commands=None)

    @patch('mist.sdk.function.watchedInsert')
    async def test_corePut_stores_data_in_table(self, mock_watchedInsert):
        stack = []

        await corePut("FOO", "one", "two", "three", "four", "five", stack=stack, commands=None)

        mock_watchedInsert.assert_called_once_with("FOO", stack, ["one", "two", "three", "four", "five"], fields=None)

    @patch('mist.sdk.function.watchedInsert')
    async def test_corePut_stores_list_data_as_string_in_table(self, mock_watchedInsert):
        stack = []

        await corePut("FOO", ["one", "two"], "three", stack=stack, commands=None)

        mock_watchedInsert.assert_called_once_with("FOO", stack, ['["one", "two"]', "three"], fields=None)

######
###### corePutData
######
    async def test_corePutData_raises_MistException_when_no_table_given(self):
        expected = "A table is needed"

        with self.assertRaisesRegex(MistException, expected):
            await corePutData(None, None, stack=[], commands=None)
            await corePutData("", None, stack=[], commands=None)

    async def test_corePutData_raises_MistException_when_no_data_given(self):
        expected = "Data items to store needed"

        with self.assertRaisesRegex(MistException, expected):
            await corePutData("FOO", None, stack=[], commands=None)

    async def test_corePutData_raises_TypeError_when_data_isnotdict(self):
        expected = "Data must come in a dictionary"

        with self.assertRaisesRegex(TypeError, expected):
            await corePutData("FOO", ["foo"], stack=[], commands=None)
            await corePutData("FOO", "foo", stack=[], commands=None)

    @patch('mist.sdk.function.watchedInsert')
    async def test_corePutData_stores_list_data_as_string_in_table(self, mock_watchedInsert):
        stack = []
        data = {"one": "1", "two": ["1", "2"]}

        await corePutData("FOO", data, stack=stack, commands=None)

        mock_watchedInsert.assert_called_once_with("FOO", stack, ["1", '["1", "2"]'], ["one", "two"])

######
###### coreSend
######
    @patch('mist.sdk.function.helpers.get_key')
    async def test_coreSend_looks_for_target_stream(self, mock_getKey):
        streamKey = "targetStream"
        msg = "FOO"
        stack = []

        await coreSend(msg, stack=stack, commands=None)

        mock_getKey.assert_called_once_with(streamKey, stack)

    @patch('mist.sdk.function.helpers.get_key')
    async def test_coreSend_does_nothing_if_no_value_given(self, mock_getKey):
        streamKey = "targetStream"
        stack = []

        await coreSend(None, stack=stack, commands=None)

        mock_getKey.assert_not_called()

    @patch('mist.sdk.function.streams.send')
    @patch('mist.sdk.function.helpers.get_key')
    async def test_coreSend_sends_if_theres_stream(self, mock_getKey, mock_streams_send):
        streamKey = "targetStream"
        streamName = "myStream"
        msg = "FOO"
        stack = []
        mock_getKey.return_value = streamName

        await coreSend(msg, stack=stack, commands=None)

        mock_getKey.assert_called_once_with(streamKey, stack)
        mock_streams_send.assert_called_once_with(streamName, msg)

    @patch('mist.sdk.function.streams.send')
    @patch('mist.sdk.function.helpers.get_key')
    async def test_coreSend_dont_send_if_theres_no_stream(self, mock_getKey, mock_streams_send):
        curStream = "targetStream"
        stack = []
        mock_getKey.side_effect = MistUndefinedVariableException()

        await coreSend("FOO", stack=stack, commands=None)

        mock_getKey.assert_called_once_with(curStream, stack)
        mock_streams_send.assert_not_called()

######
###### parseInt
######
    def test_parseInt_raises_exception_when_non_string_given(self):
        tests = [{}, []]

        for t in tests:
            with self.assertRaises(TypeError):
                parseInt(t)

    def test_parseInt_raises_exception_when_no_parseable_integer_given(self):
        tests = ["{}", "[]", "hola", "1234.56"]

        for t in tests:
            with self.assertRaises(ValueError):
                parseInt(t)

    def test_parseInt_parses_integers_given(self):
        tests = [["0", 0], ("-1", -1), ("123456", 123456)]

        for t in tests:
            r = parseInt(t[0])

            self.assertEqual(r, t[1])

######
###### toString
######
    def test_toString_returns_string_representation(self):
        tests = [[0, "0"], (-1, "-1"), (1234.56, "1234.56")]

        for t in tests:
            r = toString(t[0])

            self.assertEqual(r, t[1])
