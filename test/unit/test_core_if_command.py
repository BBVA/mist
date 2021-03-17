from unittest import (IsolatedAsyncioTestCase, TestCase, skip)
from unittest.mock import (patch, call)

from mist.lang.classes import (IfCommand, command_runner)

class IfBranch:
    def __init__(self, cond, comm):
        self.condition = cond
        self.commands = comm

class BooleanFunctionsTest(IsolatedAsyncioTestCase):

    @patch('mist.lang.classes.command_runner')
    async def test_executes_if_branch_when_its_condition_is_true(self, mock_cmd_run):
        t = "test"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', return_value = True) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, c), [], None)
            await cmd.run(s)

        mck_eval.assert_called_once_with(t, s)
        mock_cmd_run.assert_called_once_with(c, s)

    @patch('mist.lang.classes.command_runner')
    async def test_doesnt_execute_when_if_condition_false_and_not_else_exist(self, mock_cmd_run):
        t = "test"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', return_value = False) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, []), [], None)
            await cmd.run(s)

        mck_eval.assert_called_once_with(t, s)
        mock_cmd_run.assert_not_called()

    @patch('mist.lang.classes.command_runner')
    async def test_executes_else_branch_when_if_condition_is_false(self, mock_cmd_run):
        t = "test"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', return_value = False) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, []), [], IfBranch(None, c))
            await cmd.run(s)

        mck_eval.assert_called_once_with(t, s)
        mock_cmd_run.assert_called_once_with(c, s)

    @patch('mist.lang.classes.command_runner')
    async def test_try_all_elsif_branches_when_no_condition_meets_and_run_else(self, mock_cmd_run):
        t = "if"
        t1 = "elsif1"
        t2 = "elsif2"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', return_value = False) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, []), [IfBranch(t1, []), IfBranch(t2, [])], IfBranch(None, c))
            await cmd.run(s)

        mck_eval.assert_has_calls([call(t, s), call(t1, s), call(t2, s)])
        mock_cmd_run.assert_called_once_with(c, [])

    @patch('mist.lang.classes.command_runner')
    async def test_try_all_elsif_branches_when_no_condition_meets(self, mock_cmd_run):
        t = "if"
        t1 = "elsif1"
        t2 = "elsif2"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', return_value = False) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, []), [IfBranch(t1, []), IfBranch(t2, [])], None)
            await cmd.run(s)

        mck_eval.assert_has_calls([call(t, s), call(t1, s), call(t2, s)])
        mock_cmd_run.assert_not_called()

    @patch('mist.lang.classes.command_runner')
    async def test_try_exist_after_one_elsif_branch_condition_meets(self, mock_cmd_run):
        t = "if"
        t1 = "elsif1"
        t2 = "elsif2"
        c = ["cmd1", "cmd2"]
        s = []

        with patch.object(IfCommand, 'evaluate', side_effect = lambda cond, stack: True if cond == "elsif1" else False) as mck_eval:
            cmd = IfCommand(None, IfBranch(t, []), [IfBranch(t1, c), IfBranch(t2, [])], None)
            await cmd.run(s)

        mck_eval.assert_has_calls([call(t, s), call(t1, s)])
        mock_cmd_run.assert_called_once_with(c, s)
