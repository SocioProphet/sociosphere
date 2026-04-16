from __future__ import annotations

import argparse
import json
from pathlib import Path

from .events import EventSink
from .mount_agent import MountAgent, MountRequest
from .retrieval_registry import RetrievalRegistry
from .schema_refs import schema_paths
from .validator import validate_file


def cmd_validate(args: argparse.Namespace) -> int:
    schemas = schema_paths()
    if args.schema not in schemas:
        print(json.dumps({"error": f"unknown schema {args.schema!r}", "known": sorted(schemas)}))
        return 2
    errors = validate_file(args.instance, schemas[args.schema])
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


def cmd_register_demo(args: argparse.Namespace) -> int:
    registry = RetrievalRegistry()
    sink = EventSink(Path(args.events_file))
    agent = MountAgent(registry, sink)
    response = agent.register_mount(
        MountRequest(
            mount_name=args.mount_name,
            backend_type=args.backend_type,
            resolved_path_or_handle=args.path,
            node_ref=args.node_ref,
            rw_mode=args.rw_mode,
            capacity_bytes=args.capacity_bytes,
            workspace_ref=args.workspace_ref,
            dataset_ref=args.dataset_ref,
            pipeline_version=args.pipeline_version,
            policy_bundle_ref=args.policy_bundle_ref,
            principal=args.principal,
        )
    )
    print(json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o)), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fabric")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-json")
    validate.add_argument("schema", help="schema key, e.g. manifest.v1")
    validate.add_argument("instance", help="path to JSON instance file")
    validate.set_defaults(func=cmd_validate)

    demo = sub.add_parser("register-demo")
    demo.add_argument("--mount-name", required=True)
    demo.add_argument("--backend-type", required=True)
    demo.add_argument("--path", required=True)
    demo.add_argument("--node-ref", default="node.local")
    demo.add_argument("--rw-mode", default="rw")
    demo.add_argument("--capacity-bytes", type=int, default=0)
    demo.add_argument("--workspace-ref", required=True)
    demo.add_argument("--dataset-ref", required=True)
    demo.add_argument("--pipeline-version", default="v1")
    demo.add_argument("--policy-bundle-ref", default="policy/default")
    demo.add_argument("--principal", default="operator")
    demo.add_argument("--events-file", default="/tmp/fabric-events.ndjson")
    demo.set_defaults(func=cmd_register_demo)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
