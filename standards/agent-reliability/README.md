# Agent Reliability Governance Queue

SocioSphere owns the cross-repo review queue contract for the SourceOS Agent Reliability Control Plane.

This contract turns disconnected evidence artifacts into visible review items:

- PolicyFabric `BreakGlassOverride` artifacts become `break-glass-approval` queue items.
- MemoryMesh `AgentLearningProposal` artifacts become `memory-learning-review` queue items.
- AgentPlane stop-gate failures can become `stop-gate-waiver` queue items.
- External draft/publication artifacts can become `external-action-review` queue items.

## Files

- `governance-queue.schema.v0.1.json` — queue schema.
- `examples/governance-queue.example.v0.1.json` — example queue with break-glass and memory-learning review items.
- `../../tools/validate_agent_reliability_governance_queue.py` — dependency-free validator.

## Validate

```bash
make agent-reliability-governance-queue-validate
```

or run it as part of the normal SocioSphere standards validation:

```bash
make validate
```

## Required safety posture

Example queue items must remain pending by default. Approval and rejection are later governance actions and should produce their own evidence.

Every item requires:

- source artifact system/repo/kind/ref;
- risk classification;
- required reviewers;
- evidence references;
- policy decision references.

Break-glass approval items must reference PolicyFabric `BreakGlassOverride` artifacts and carry high or critical risk. Memory learning review items must reference MemoryMesh `AgentLearningProposal` artifacts and use `actionClass=memory`.
