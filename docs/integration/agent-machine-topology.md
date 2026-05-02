# SourceOS Agent Machine topology lane

SourceOS Agent Machine is the cross-host local workspace lane for Mac, Windows, and Linux operator machines.

It connects local terminal, browser, editor, and governed agent-tool surfaces to an internal Podman-backed or native agent workspace through explicit SourceOS contracts, Agent Registry grants, AgentPlane evidence, and Sociosphere topology validation.

## Machine-readable topology

The machine-readable topology lane lives at:

```text
registry/agent-machine-topology.yaml
```

This file records:

- repo ownership boundaries;
- dependency direction;
- local mount defaults;
- TopoLVM storage semantics;
- security invariants;
- validation expectations.

## Repo ownership

| Repo | Role |
|---|---|
| `SourceOS-Linux/sourceos-spec` | Canonical contracts: AgentMachineLocalDataPlane, AgentMachineMountPolicy, SecureHostInterfaceProfile, HostInterfaceGrant, TopoLVMPlacementProfile. |
| `SourceOS-Linux/sourceos-devtools` | Local `sourceosctl` implementation for mount planning, dry-run initialization, inspection, and evidence import. |
| `SocioProphet/agentplane` | Backend intent, placement/run/replay evidence, and AgentMachineMountEvidence. |
| `SocioProphet/agent-registry` | Non-human identity, terminal/browser/editor/agent-tool grants, revocation, and expiration. |
| `SourceOS-Linux/agent-term` | Matrix-first operator shell and event surface. |
| `SourceOS-Linux/sourceos-shell` | Product UX posture for Terminal Door, Browser Door, Editor Door, and Agent Tool Door. |
| `SocioProphet/prophet-cli` | Facade commands that delegate to sourceosctl and AgentTerm. |
| `SocioProphet/homebrew-prophet` | Mac-first Homebrew install surface for sourceosctl and AgentTerm. |
| `SocioProphet/topolvm` | Linux cluster-local TopoLVM storage backend reference. |

## Canonical mount roots

| Purpose | Host path | Agent path | Posture |
|---|---|---|---|
| Code / repositories | `~/dev` | `/workspace/dev` | read/write; explicit root |
| Generated docs/reports | `~/Documents/SourceOS/agent-output` | `/workspace/output` | read/write; explicit root |
| Browser downloads | `~/Downloads/SourceOS/agent-downloads` | `/workspace/downloads` | browser read/write; agent read-only |

Whole-home mounts are forbidden. Sensitive host paths such as `.ssh`, `.gnupg`, browser profiles, keychains, cloud credentials, token stores, and password stores are denied by default.

## TopoLVM semantics

TopoLVM is the Linux cluster-local backend for the same logical mount contract.

It provides topology-aware node-local persistent volumes. It is not a cross-node shared filesystem. If SourceOS later needs cross-node shared semantics, those should be represented by a replication or mesh storage layer above or adjacent to TopoLVM.

## App surfaces

Mac app surfaces such as Notes, Reminders, Photos, Voice Memos, and TextEdit-style documents should not be raw default mounts.

They belong to future App Doors with explicit grants, app-specific APIs or export/import flows, and evidence records.

## Validation intent

Sociosphere validation should eventually flag:

- `$HOME` wholesale mounts;
- sensitive host path mounts;
- unscoped host Downloads mounts;
- TopoLVM profiles claiming cross-node shared storage;
- Agent Machine runs that lack AgentPlane evidence;
- platform-specific Podman implementation leaking into AgentTerm or Sociosphere.

## Status

This integration is contract/topology wiring. Runtime implementation lives in the owning downstream repos.
