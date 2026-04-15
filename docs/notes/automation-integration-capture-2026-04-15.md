# Automation & Integration Capture — 2026-04-15

This note captures the current, robust posture for cross-org automation + integration, and snapshots **public** repositories updated in the last 30 days across:

- SocioProphet
- SociOS-Linux
- SourceOS-Linux

Private repositories are intentionally omitted from this public document.

## Canonical decision (robust option)

We use a 3-tier topology:

1) Component repos are canonical (implementation source-of-truth)
   - Examples: `SocioProphet/agentplane`, `SociOS-Linux/agentos-spine`, `SourceOS-Linux/sourceos-spec`, `SourceOS-Linux/openclaw`.

2) Integration repo is canonical for workspace/locks, topology, registry metadata
   - This repo: `SocioProphet/sociosphere`.

3) Platform repo is canonical for the runnable product surface
   - `SocioProphet/socioprophet` remains the main platform surface that unifies web + AgentOS + agentplane integration.

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

## Immediate alignment tasks

1) Refresh entries in `manifest/workspace.toml` + `manifest/workspace.lock.json` for active repos and their roles.
2) Update `governance/CANONICAL_SOURCES.yaml` for AgentOS interfaces, agentplane bundle schema/validators, and registry allowlists.
3) Track dedup for overlapping repo names across orgs (example: `cloudshell-fog`).
4) If any repo vendors code from another, pin upstream SHA and fail CI on drift.
