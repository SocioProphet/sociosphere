# Workspace manifest cleanup tranche — 2026-04-09

This branch captures the smallest no-churn cleanup identified during live connector review.

## Verified defects

1. `manifest/workspace.toml` maps `socioprophet_web` to `https://github.com/SocioProphet/socioprophet` with `ref = "main"`, but the live repository does not expose a `main` branch.
2. `manifest/workspace.lock.json` repeats the same `socioprophet_web` ref mismatch.
3. `manifest/workspace.toml` contains a duplicate `agentplane` entry. The canonical `execution-plane` entry should retain the trust metadata, and the later duplicate entry should be removed.

## Intended direct fix

- change `socioprophet_web` from `ref = "main"` to `ref = "master"` in both manifest and lock
- fold trust metadata into the canonical `agentplane` entry
- remove the duplicate `agentplane` block

## Why this note exists

The connector session allowed branch creation and full repo verification, but tracked-file overwrite was blocked by the current safety layer. This note preserves the exact tranche in GitHub without claiming the tracked files were updated here.
