#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from workspace_fabric_state_machine import WorkspaceFabricStateMachine, StateMachineError


class WorkspaceFabricStateMachineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.machine = WorkspaceFabricStateMachine.from_file()

    def test_valid_transition(self) -> None:
        result = self.machine.transition("ACTIVE", "DEGRADED")
        self.assertTrue(result.accepted)
        self.assertEqual(result.from_state, "ACTIVE")
        self.assertEqual(result.to_state, "DEGRADED")

    def test_invalid_transition(self) -> None:
        with self.assertRaises(StateMachineError):
            self.machine.transition("ACTIVE", "DISCOVERED")

    def test_trigger_mismatch(self) -> None:
        with self.assertRaises(StateMachineError):
            self.machine.transition("ACTIVE", "DEGRADED", trigger="wrong_trigger")


if __name__ == "__main__":
    unittest.main()
