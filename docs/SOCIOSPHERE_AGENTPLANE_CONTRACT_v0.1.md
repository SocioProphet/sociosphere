# Sociosphere -> Agentplane Contract v0.1

## Purpose
Define the seam between the workspace controller (`sociosphere`) and the execution control plane (`agentplane`).

The rule is simple:
- `sociosphere` owns workspace composition, lock/pin truth, task execution reports, and protocol compatibility results.
- `agentplane` owns bundle validation, placement, run, and replay.
- The handoff happens through normalized artifacts and a generated `Bundle`, not through ad hoc repo introspection.

## Contract shape

### Upstream artifacts emitted by `sociosphere`
These artifacts are generated before deployment/execution and live under a stable output directory such as:

`artifacts/workspace/<run-id>/`

#### 1. WorkspaceInventoryArtifact
Purpose: snapshot the materialized workspace and its drift state.

Required fields:
- `kind = "WorkspaceInventoryArtifact"`
- `workspace.name`
- `workspace.version`
- `generatedAt`
- `manifestDigest`
- `lockDigest`
- `repos[]` with:
  - `name`
  - `role`
  - `localPath`
  - `url`
  - `ref`
  - `rev`
  - `headRev`
  - `status`
  - `lockDrift`

#### 2. LockVerificationArtifact
Purpose: record whether workspace pins are resolvable, normalized, and drift-free.

Required fields:
- `kind = "LockVerificationArtifact"`
- `generatedAt`
- `result` (`pass` or `fail`)
- `unresolvedRepos[]`
- `driftedRepos[]`
- `messages[]`

#### 3. TaskRunArtifact
Purpose: report a runner task executed against a selected repo.

Required fields:
- `kind = "TaskRunArtifact"`
- `generatedAt`
- `repo.name`
- `repo.role`
- `task`
- `contractType` (`make`, `just`, `task`, `script`, `none`)
- `command[]`
- `startedAt`
- `finishedAt`
- `exitCode`
- `stdoutRef`
- `stderrRef`

#### 4. ProtocolCompatibilityArtifact
Purpose: record adapter or fixture compatibility checks.

Required fields:
- `kind = "ProtocolCompatibilityArtifact"`
- `generatedAt`
- `fixtureSet`
- `subject`
- `result` (`pass`, `fail`, `warn`)
- `messages[]`

## Bundle generation
`Sociosphere` may generate an `agentplane` bundle from normalized workspace state, but it must not define a separate runtime control format.

The generated bundle must satisfy `agentplane` bundle schema requirements:
- `apiVersion`
- `kind = "Bundle"`
- `metadata.name`
- `metadata.version`
- `metadata.createdAt`
- `spec.vm`
- `spec.policy`
- `spec.secrets`
- `spec.artifacts`
- `spec.smoke`

### Recommended mapping
- workspace deploy target -> `metadata.name`
- normalized deploy version -> `metadata.version`
- generation timestamp -> `metadata.createdAt`
- locked source revision -> `metadata.source.git.rev`
- license/compliance gate result -> `metadata.licensePolicy`
- artifact root -> `spec.artifacts.outDir`
- deployment lane -> `spec.policy.lane`
- workspace/deploy timeout -> `spec.policy.maxRunSeconds`
- policy selection -> `spec.policy.policyPackRef` + `policyPackHash`
- required secret refs -> `spec.secrets.*`
- smoke entrypoint -> `spec.smoke.script`
- backend choice -> `spec.vm.backendIntent`
- executor pin (optional) -> `spec.executor.ref`

## Downstream artifacts emitted by `agentplane`
Once the bundle is handed off, `agentplane` is the system of record for execution-plane evidence:
- `ValidationArtifact`
- `PlacementDecision`
- `RunArtifact`
- `ReplayArtifact`

## Seams and responsibilities
`Sociosphere` must not:
- choose executors by probing fleet state on its own,
- emit alternate runtime placement formats,
- inline secrets into generated bundles,
- bypass bundle validation.

`Agentplane` must not:
- rediscover workspace composition by scanning sibling repos,
- reinterpret manifest roles that were already normalized upstream,
- treat runner logs as the only source of evidence when structured upstream artifacts exist.

## Immediate implementation targets
- `tools/runner/runner.py`: emit structured upstream artifacts.
- `protocol/agentplane/v0/*.schema.json`: hold the JSON schemas for upstream artifacts.
- `agentplane`: accept generated bundles plus references to upstream workspace artifacts.

## Versioning guidance
- Keep this contract versioned independently from individual repo release versions.
- Bump the contract when artifact structure or required fields change.
