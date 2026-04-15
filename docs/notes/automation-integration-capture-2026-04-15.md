# Automation & Integration Capture — 2026-04-15

This note captures the current, robust posture for cross-org automation + integration, and snapshots **public** repositories that have been updated in the last 30 days across:

- SocioProphet
- SociOS-Linux
- SourceOS-Linux

Note: private repositories are intentionally omitted from this public document.

## Canonical decision (robust option)

We use a 3-tier topology:

1) **Component repos are canonical** (implementation source-of-truth)
   - Examples: `SocioProphet/agentplane`, `SociOS-Linux/agentos-spine`, `SourceOS-Linux/sourceos-spec`, `SourceOS-Linux/openclaw`.

2) **Integration repo is canonical for workspace/locks, topology, registry metadata**
   - This repo: `SocioProphet/sociosphere`.

3) **Platform repo is canonical for the runnable product surface**
   - `SocioProphet/socioprophet` remains the main platform surface that unifies web + AgentOS + agentplane integration.

### Why this is the most robust option

- Prevents silent drift: component repos remain authoritative.
- Integration is reproducible: sociosphere pins exact revisions via manifest + lock.
- Product remains cohesive: socioprophet can vendor or reference pinned components, but must align to canonical SHAs.

## Public repositories updated in the last 30 days

### SocioProphet (pushed since 2026-03-16)

- api-contracts
- contractforge
- socioprophet-standards-storage
- memory-mesh
- prophet-platform-standards
- prophet-platform-fabric-mlops-ts-suite
- sociosphere
- tritfabric
- prophet-cli
- socioprophet-standards-knowledge
- sherlock-search
- prophet-platform
- TriTRPC
- policy-fabric
- synapseiq
- socioprophet-agent-standards
- cloudshell-fog
- agentplane
- global-devsecops-intelligence
- delivery-excellence-automation
- agent-inbox
- human-digital-twin
- prophet-workspace
- semantic-serdes
- alexandrian-academy
- slash-topics
- manifests
- delivery-excellence
- meshrush
- gaia-world-model
- socioprophet
- ontogenesis
- hyperdiscovery
- Heller-Winters-Theorem
- delivery-excellence-innersource
- socioprophet-docs
- delivery-excellence-bounties
- cairnpath-mesh
- delivery-excellence-boards
- mcp-a2a-zero-trust
- exodus
- mempalace
- hermes-agent
- agent-skills
- OmniVoice
- identity-is-prime-reference
- graphbrain-contract
- usol-space-library

### SociOS-Linux (pushed since 2026-03-16)

- source-os
- Zettlr
- SourceOS
- cloudshell-fog
- agentos-starter
- socioslinux-web
- workstation-contracts
- agentos-spine
- imagelab
- hyperswarm-agent-composable-cluster-scale-up

### SourceOS-Linux (pushed since 2026-03-16)

- sourceos-spec
- openclaw
- MMTEB-MCP

## Where integration work goes

- **SocioProphet/sociosphere**: canonical registry + manifest/lock + topology policy; should track the above repos and their roles.
- **SocioProphet/socioprophet**: productized integration surface; must remain compatible with canonical component versions.
- **SociOS-Linux/agentos-spine**: Linux-side integration spine; keep Linux substrate and interface/registry lanes aligned.
- **SourceOS-Linux/sourceos-spec**: typed contracts + shared vocabulary; promote stable interfaces here once formalized.

## Immediate alignment tasks

1) Add/refresh entries in `manifest/workspace.toml` + `manifest/workspace.lock.json` for every active repo above.
2) Update `governance/CANONICAL_SOURCES.yaml` to declare canonical sources for:
   - AgentOS interfaces
   - agentplane bundle schema + validators
   - registry/policy allowlists
3) Add a dedup entry for overlapping names across orgs (example: `cloudshell-fog`).
4) If any repo vendors code from another, pin the upstream SHA and fail CI on drift.
