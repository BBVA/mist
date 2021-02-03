from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase

from mist.sdk.function import (functions, corePrint, coreAbort)
from mist.sdk.exceptions import (MistAbortException)


class CoreFunctionsTest(TestCase):

######
###### Check for exported functions
######
    def test_all_functions_are_exported(self):
        ef = [("print", corePrint), ("abort", coreAbort)]

        for i in ef:
            self.assertTrue(i[0] in functions and functions[i[0]]["commands"] == i[1] and functions[i[0]]["native"], f"{i} not exported")

    @patch('mist.sdk.function.print')
    @patch('mist.sdk.function.helpers.get_id')
    def test_CorePrint_call_python_print_with_all_its_params(self, mock_getId, mock_print):
        stack = []
        mock_getId.side_effect = lambda id, stack: id

        corePrint("one", "two", "three", "four", "five", stack=stack, commands=None)

        mock_print.assert_called_with("one", "two", "three", "four", "five")

    def test_coreAbort_raises_exception_when_no_reason_given(self):
        expected = "Abort reached"

        with self.assertRaisesRegex(MistAbortException, expected):
            coreAbort([], [])
            coreAbort(None, [], [])
            coreAbort("", [], [])

    def test_coreAbort_raises_exception_with_reason_given(self):
        expected = "Abort forced"

        with self.assertRaisesRegex(MistAbortException, expected):
            coreAbort(expected, [], [])
