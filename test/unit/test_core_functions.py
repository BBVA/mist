from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase, skip

from mist.lang.function import (functions, corePrint, coreAbort,
                                parseInt, toString)
from mist.lang.exceptions import (MistException, MistAbortException, MistUndefinedVariableException)


class CoreFunctionsTest(IsolatedAsyncioTestCase):

######
###### Check for exported functions
######
    def test_all_functions_are_exported(self):
        ef = [("print", corePrint), ("abort", coreAbort)]

        for i in ef:
            self.assertTrue(i[0] in functions and functions[i[0]]["commands"] == i[1] and functions[i[0]]["native"], f"{i} not exported")
            if len(i) > 2:
                self.assertEqual(i[2], functions[i[0]]["async"])

######
###### corePrint
######
    @patch('mist.lang.function.print')
    @patch('mist.lang.function.helpers.get_id')
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
