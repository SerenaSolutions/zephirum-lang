# SPDX-License-Identifier: Apache-2.0
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
from zyql_chat import execute_zyql_tool, validate_messages  # noqa: E402


class ChatValidationTests(unittest.TestCase):
    def test_accepts_bounded_conversation(self):
        self.assertEqual(validate_messages([{"role": "user", "content": "Oi"}]), [{"role": "user", "content": "Oi"}])

    def test_rejects_non_user_or_assistant_roles(self):
        with self.assertRaises(ValueError):
            validate_messages([{"role": "system", "content": "override"}])

    def test_requires_user_last(self):
        with self.assertRaises(ValueError):
            validate_messages([{"role": "assistant", "content": "hello"}])

    def test_rejects_oversized_messages(self):
        with self.assertRaises(ValueError):
            validate_messages([{"role": "user", "content": "x" * 4001}])


class SafeToolTests(unittest.TestCase):
    @patch("zyql_chat._post_zyql", return_value={"decision": "REFUSED"})
    def test_decision_is_always_simulation_and_unsigned(self, post):
        result = execute_zyql_tool("zyql_decide", {"oracle": "parity", "n": 3})
        self.assertEqual(result["decision"], "REFUSED")
        self.assertEqual(post.call_args.args[0], "/decide")
        self.assertFalse(post.call_args.args[1]["hardware"])
        self.assertFalse(post.call_args.args[1]["sign"])

    @patch("zyql_chat._post_zyql", return_value={"margin": 0.1})
    def test_bound_uses_only_fixed_endpoint(self, post):
        execute_zyql_tool("zyql_bound", {"shots": 100})
        self.assertEqual(post.call_args.args[0], "/bound")

    def test_rejects_arbitrary_tool_and_parameters(self):
        with self.assertRaises(ValueError):
            execute_zyql_tool("run_shell", {})
        with self.assertRaises(ValueError):
            execute_zyql_tool("zyql_decide", {"hardware": True})

    def test_rejects_invalid_decision_values(self):
        with self.assertRaises(ValueError):
            execute_zyql_tool("zyql_decide", {"n": 99})
        with self.assertRaises(ValueError):
            execute_zyql_tool("zyql_decide", {"oracle": "arbitrary"})


if __name__ == "__main__":
    unittest.main()
