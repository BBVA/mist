from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase, TestCase

from mist.sdk.function import (corePrint)


class CoreFunctionsTest(TestCase):

    @patch('mist.sdk.function.print')
    @patch('mist.sdk.function.helpers.get_id')
    def test_CorePrint_call_python_print_with_all_its_params(self, mock_getId, mock_print):
        stack = []
        mock_getId.side_effect = lambda id, stack: id

        corePrint("one", "two", "three", "four", "five", stack=stack, commands=None)

        mock_print.assert_called_with("one", "two", "three", "four", "five")
