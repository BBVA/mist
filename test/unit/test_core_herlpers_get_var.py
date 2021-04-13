import unittest

from unittest.mock import patch

from mist.lang.herlpers import get_var

from test.utilTest import *


class Get_var_Test(unittest.TestCase):

    def test_returns_True_when_given_True_or_Success_string(self):
        params = [ "True", "Success" ]

        for p in params:
            ret = get_var(p, [])
            self.assertTrue(ret)

    def test_returns_False_when_given_False_or_Error_string(self):
        params = [ "False", "Error" ]

        for p in params:
            ret = get_var(p, [])
            self.assertFalse(ret)

    def test_returns_integer_when_given_integer(self):
        result = 45

        ret = get_var(result, [])

        self.assertEqual(result, ret)

    def test_returns_variable_value_when_given_variable_name(self):
        var_name = "myVar"
        var_value = "FOO"
        init_mist()
        create_variable(var_name, var_value)

        ret = get_var(var_name, get_mistStack())

        self.assertEqual(var_value, ret)
