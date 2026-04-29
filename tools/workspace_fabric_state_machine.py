#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_MACHINE = ROOT / "protocol" / "workspace-fabric" / "v0" / "fixtures" / "state-machine.example.json"


class StateMachineError(ValueError):
    """Raised when a workspace-fabric state transition is invalid."""


@dataclass(frozen=True)
class TransitionResult:
    from_state: str
    to_state: str
    trigger: str
    accepted: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "trigger": self.trigger,
            "accepted": self.accepted,
        }


class WorkspaceFabricStateMachine:
    def __init__(self, states: Iterable[str], transitions: Iterable[dict[str, str]]) -> None:
        self.states = set(states)
        self.transitions = {
            (edge["from"], edge["to"]): edge["trigger"]
            for edge in transitions
        }

    @classmethod
    def from_file(cls, path: Path = DEFAULT_STATE_MACHINE) -> "WorkspaceFabricStateMachine":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("api_version") != "sourceos.fabric.mount/v0.1":
            raise StateMachineError("unsupported workspace-fabric api_version")
        if payload.get("kind") != "MountStateMachine":
            raise StateMachineError("unsupported state-machine kind")
        return cls(payload["states"], payload["transitions"])

    def assert_state(self, state: str) -> None:
        if state not in self.states:
            raise StateMachineError(f"unknown state: {state}")

    def allowed(self, from_state: str, to_state: str) -> bool:
        self.assert_state(from_state)
        self.assert_state(to_state)
        return (from_state, to_state) in self.transitions

    def transition(self, from_state: str, to_state: str, trigger: str | None = None) -> TransitionResult:
        self.assert_state(from_state)
        self.assert_state(to_state)
        key = (from_state, to_state)
        if key not in self.transitions:
            raise StateMachineError(f"illegal transition: {from_state} -> {to_state}")
        expected_trigger = self.transitions[key]
        if trigger is not None and trigger != expected_trigger:
            raise StateMachineError(
                f"trigger mismatch for {from_state} -> {to_state}: expected {expected_trigger}, got {trigger}"
            )
        return TransitionResult(
            from_state=from_state,
            to_state=to_state,
            trigger=expected_trigger,
            accepted=True,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workspace-fabric-state")
    parser.add_argument("from_state")
    parser.add_argument("to_state")
    parser.add_argument("--trigger")
    parser.add_argument("--state-machine", default=str(DEFAULT_STATE_MACHINE))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    machine = WorkspaceFabricStateMachine.from_file(Path(args.state_machine))
    result = machine.transition(args.from_state, args.to_state, args.trigger)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
