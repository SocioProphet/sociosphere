# KubeEdge Optional Edge Substrate Governance

Status: v0 governance contract
Owner surface: SocioSphere

## Purpose

This document defines how KubeEdge may be used as an optional Kubernetes-native edge substrate in the GAIA / OFIF / MeshLab / Control Tower program.

KubeEdge is not the default edge architecture for every deployment. It is a governed substrate option for managed fleets where Kubernetes-native orchestration, cloud-edge sync, edge autonomy, and edge-device management are the right operational model.

## Core decision

KubeEdge is optional.

Do not make KubeEdge mandatory for:

- local-only SourceOS hosts;
- small home or single-room deployments;
- early Smart Spaces experiments;
- non-Kubernetes device fabrics;
- offline-first laptop/appliance workflows.

Use KubeEdge when the deployment needs Kubernetes-native edge fleet management.

## Authority boundaries

| Concern | Authority |
| --- | --- |
| Host lifecycle, boot, recovery, update, rollback | SourceOS / nlboot |
| Edge Kubernetes orchestration substrate | KubeEdge when selected |
| Workspace, fleet, site, policy, readiness governance | SocioSphere |
| Field/device event envelope | OFIF |
| World/asset/geospatial model | GAIA |
| Local state sampling/percolation | Lampstand |
| Graph-native agent operation | MeshRush |
| Governed execution/replay | Agentplane |
| Runtime provenance/admission | Lattice Forge |
| Discovery/search | Sherlock |

## Governance rule

A KubeEdge deployment is not accepted until SocioSphere can register:

- workspace/site ref;
- fleet ref;
- edge node identity;
- host lifecycle authority;
- KubeEdge role and version;
- CloudCore/EdgeCore topology;
- device twin usage state;
- network posture;
- autonomy expectations;
- workload policy;
- rollback policy;
- evidence/provenance refs.

## SourceOS / nlboot relationship

SourceOS and nlboot own the machine lifecycle.

KubeEdge may run on top of a SourceOS-managed node, but it must not replace:

- host attestation;
- boot/recovery policy;
- update/rollback mechanism;
- enrollment identity;
- local break-glass/recovery path;
- SourceOS release tracking.

## KubeEdge integration profile

When selected, KubeEdge should be represented as:

```text
SourceOS/nlboot managed host
  -> SocioSphere registered edge node
  -> KubeEdge EdgeCore where Kubernetes edge orchestration is required
  -> OFIF device/event envelopes
  -> GAIA world/asset model
  -> MeshRush graph operation
  -> Agentplane governed action
  -> Sherlock/Lattice/SocioSphere evidence and readiness records
```

## Required readiness states

- `not-selected`: KubeEdge is not used.
- `candidate`: deployment may benefit from KubeEdge.
- `planned`: topology and policy drafted.
- `registered`: node/site/fleet registered in SocioSphere.
- `validated`: topology, policy, autonomy, and event bindings validated.
- `operational`: active governed KubeEdge deployment.
- `blocked`: unresolved identity, networking, policy, or safety issue.

## Required records

Candidate future contracts:

- `KubeEdgeSubstrateProfile`
- `EdgeNodeEnrollmentRecord`
- `CloudEdgeTopologyRecord`
- `DeviceTwinBindingRecord`
- `EdgeAutonomyPolicy`
- `EdgeWorkloadPolicy`
- `EdgeRollbackPlan`
- `EdgeReadinessReport`

Do not place these schemas until the owning repo is selected.

Interim owner for this governance decision: SocioSphere.

## Policy requirements

KubeEdge integration must define:

1. whether edge nodes may operate offline;
2. what workloads may continue during cloud-edge partition;
3. whether device-twin state can trigger local action;
4. what actions require Agentplane approval;
5. how OFIF events are emitted from edge/device state;
6. how GAIA world-state is updated;
7. how rollback works if an edge workload misbehaves;
8. how source-exposure and privacy policies apply;
9. whether Smart Spaces privacy constraints are involved;
10. how evidence is indexed in Sherlock.

## Smart Spaces relationship

Smart Spaces / Built Environment remains a domain-home-open decision.

KubeEdge may support smart buildings, campuses, hotels, classrooms, or facilities, but KubeEdge does not decide the domain home.

Do not create Smart Spaces implementation schemas just because KubeEdge support exists.

## Home-scale warning

For small home or local-first deployments, KubeEdge may be too heavy.

Prefer local SourceOS + Home Assistant/Matter/Thread/MQTT integration patterns unless there is a clear fleet-management, Kubernetes-native, or edge-autonomy requirement.

## Acceptance criteria

A KubeEdge optional-substrate slice is acceptable when:

- SocioSphere records that KubeEdge is selected for a specific fleet/site;
- SourceOS/nlboot remains the host lifecycle authority;
- CloudCore/EdgeCore topology is recorded;
- edge autonomy policy is recorded;
- device-twin binding rules are recorded if device twins are used;
- OFIF event binding is defined;
- Agentplane approval boundaries are defined;
- Sherlock discovery/evidence refs exist;
- rollback policy exists;
- Smart Spaces domain boundaries are not bypassed.

## Non-goals

- Do not make Kubernetes required for every edge deployment.
- Do not bypass SourceOS host lifecycle.
- Do not bypass Agentplane for actuation.
- Do not treat DeviceTwin state as automatically trusted world-state.
- Do not create a Smart Spaces repo by implication.
- Do not add Lattice runtime assets until executable runtime boundaries and admission criteria exist.

## First implementation target

The first implementation should be governance-only:

1. add a capability-map validation lane for KubeEdge optional substrate;
2. add a change-propagation rule for KubeEdge governance docs;
3. add candidate contract names without schema placement;
4. defer implementation until a concrete fleet/site use case exists.
