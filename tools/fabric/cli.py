from __future__ import annotations

import argparse
import json
from pathlib import Path

from .connectors.drive import DriveExecutor
from .connectors.hyper import HyperExecutor
from .connectors.s3 import S3Executor
from .events import EventSink
from .integration_common import run_mount_and_connector_flow
from .mount_agent import MountAgent, MountRequest
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .retrieval_registry import RetrievalRegistry
from .schema_refs import schema_paths
from .stale_mirror_flow_harness import run_stale_mirror_flow
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


def cmd_run_harness(args: argparse.Namespace) -> int:
    mapping = {
        "drive": (DriveExecutor, "drive", "ds/demo", "demo", 1024),
        "s3": (S3Executor, "s3", "ds/demo-s3", "demo-s3", 2048),
        "hyper": (HyperExecutor, "hyper", "ds/demo-hyper", "demo-hyper", 4096),
    }
    if args.connector not in mapping:
        print(json.dumps({"error": f"unknown connector {args.connector!r}", "known": sorted(mapping)}))
        return 2
    executor_cls, connector_id, dataset_ref, mount_name, capacity_bytes = mapping[args.connector]
    result = run_mount_and_connector_flow(
        Path(args.root),
        executor_cls=executor_cls,
        connector_id=connector_id,
        dataset_ref=dataset_ref,
        mount_name=mount_name,
        capacity_bytes=capacity_bytes,
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_run_tombstone_flow(args: argparse.Namespace) -> int:
    result = run_tombstone_propagation_flow(
        Path(args.root),
        signed_tombstone=args.signed_tombstone,
        local_dirty=args.local_dirty,
        authority_mode=args.authority_mode,
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_run_authority_flow(args: argparse.Namespace) -> int:
    result = run_authority_transition_flow(
        Path(args.root),
        current_authority=args.current_authority,
        requested_authority=args.requested_authority,
        quorum_granted=args.quorum_granted,
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_run_stale_mirror_flow(args: argparse.Namespace) -> int:
    result = run_stale_mirror_flow(
        Path(args.root),
        stale_generation_gap=args.stale_generation_gap,
        policy_allow_stale=args.policy_allow_stale,
        authority_mode=args.authority_mode,
    )
    print(json.dumps(result, indent=2))
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

    harness = sub.add_parser("run-harness")
    harness.add_argument("connector", choices=["drive", "s3", "hyper"])
    harness.add_argument("--root", required=True)
    harness.set_defaults(func=cmd_run_harness)

    tombstone = sub.add_parser("run-tombstone-flow")
    tombstone.add_argument("--root", required=True)
    tombstone.add_argument("--signed-tombstone", action="store_true")
    tombstone.add_argument("--local-dirty", action="store_true")
    tombstone.add_argument("--authority-mode", default="local_first", choices=["local_first", "provider_first", "hybrid"])
    tombstone.set_defaults(func=cmd_run_tombstone_flow)

    authority = sub.add_parser("run-authority-flow")
    authority.add_argument("--root", required=True)
    authority.add_argument("--current-authority", required=True)
    authority.add_argument("--requested-authority", required=True)
    authority.add_argument("--quorum-granted", action="store_true")
    authority.set_defaults(func=cmd_run_authority_flow)

    stale = sub.add_parser("run-stale-mirror-flow")
    stale.add_argument("--root", required=True)
    stale.add_argument("--stale-generation-gap", type=int, required=True)
    stale.add_argument("--policy-allow-stale", action="store_true")
    stale.add_argument("--authority-mode", default="local_first", choices=["local_first", "provider_first", "hybrid"])
    stale.set_defaults(func=cmd_run_stale_mirror_flow)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
