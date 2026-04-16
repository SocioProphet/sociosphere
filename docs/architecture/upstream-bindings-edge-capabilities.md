# Upstream Bindings — Edge Capabilities (Draft v0.1)

## Purpose

This document records the canonical upstream projects currently informing the Linux / SourceOS
edge-capability lane, along with the disposition for each upstream: direct dependency,
wrapped dependency, maintained fork candidate, or reference-only donor.

This is intentionally narrow in scope: it covers the immediate edge-share, edge-fingerprint,
papers-intake, and future training-lane watchlist discussed for `sociosphere` capability work.

## Decision summary

| Capability / lane | Canonical upstream | Current disposition | Why |
|---|---|---|---|
| `cap.edge.share` | `KuroLabs/Airshare` | **Wrap or maintain hardened fork** | Correct UX + local-network discovery model, but unauthenticated HTTP + aging packaging make raw consumption unsafe for SourceOS |
| `cap.edge.fingerprint` | `projectdiscovery/cdncheck` | **Direct dependency + wrapper** | Small, data-driven detector with a clean provider-index seam and stable CLI/library behavior |
| `memex.papers` / papers intake | `marawangamal/papers` | **Reference implementation only** | Useful scraper + CSV ingest contract, but deployment/runtime stack is not our preferred substrate |
| future `llm.train` lane | `ServiceNow/Fast-LLM` | **Watchlist / later-lane upstream** | Active and relevant to future distributed training, but not part of the immediate edge-capability critical path |

## 1. `cap.edge.share` → `KuroLabs/Airshare`

### Why this upstream matters

`KuroLabs/Airshare` is the canonical upstream for the LAN sharing behavior we want to study:
- human-readable code words
- mDNS / Zeroconf discovery
- file + clipboard exchange
- browser fallback / HTTP gateway
- Linux / macOS / Windows CLI story

### What we verified

Airshare is packaged as a Python CLI with the console entrypoint:

```text
airshare=airshare.cli:main
```

The core implementation uses:
- `zeroconf` for `_airshare._http._tcp.local.` service registration and lookup
- `aiohttp` for sender / receiver HTTP serving
- `requests` for fetching / uploading content
- `pyperclip` for clipboard behavior

### Security / operational posture

Airshare is the **correct conceptual donor** and the **wrong final trust boundary**.

The current upstream model is:
- discovery by mDNS
- serving / upload on plain HTTP
- no built-in identity, authenticated handshake, or transport security
- broad bind behavior (`0.0.0.0`)

That means SourceOS must not ingest it as a raw dependency and pretend the job is done.

### Upstream issue signals that matter for us

The issue backlog already reflects our expected hardening needs:
- Python 3.12 build failure
- install fragility / packaging problems
- missing password protection
- requests for encrypted transfer
- VPN / wrong-interface selection
- lack of tests / coverage / CI depth
- temp zip behavior for large directories

### Required SourceOS hardening backlog

Before Airshare-like behavior is treated as a first-class SourceOS capability, the minimum backlog is:

1. Python 3.12+ / 3.13 packaging repair and deterministic build lane
2. interface selection (multi-NIC / VPN / preferred route)
3. authenticated session setup (TriTRPC hello/capabilities/policy handshake)
4. evidence / Cairn receipts for every send / receive
5. explicit file hash capture and receipt emission
6. transport hardening (or immediate wrap behind a stronger control plane)
7. tests / CI / smoke fixtures

### Ecosystem placement

- `sociosphere` owns the binding contract, wrapper semantics, lock/pin policy, and documentation
- a Linux-first hardened runtime can later graduate into a dedicated repo under the Linux org if it grows beyond a thin wrapper

## 2. `cap.edge.fingerprint` → `projectdiscovery/cdncheck`

### Why this upstream matters

`cdncheck` is already shaped correctly for our purposes:
- CLI + library usage
- compact scope
- provider intelligence driven by a compiled index
- clear separation between detector code and upstream provider data

### What we verified

The provider model is data-driven via `cmd/generate-index/provider.yaml`, which aggregates:
- provider URLs
- ASNs
- CIDRs
- common FQDN / cname mappings

This is exactly the sort of seam we want for deterministic wrapping and receipt generation.

### Disposition

Use upstream directly, but wrap it.

SourceOS / sociosphere responsibilities:
- pin version / commit
- record provider-index provenance / hash
- normalize outputs into `cap.edge.fingerprint@0.1`
- emit `cairn.edge.fingerprint@0.1` receipts

This is a **consume-and-wrap** case, not a fork-first case.

## 3. `memex.papers` / papers intake → `marawangamal/papers`

### Why this upstream matters

The forked `paperz` surface points back to `marawangamal/papers`, which provides a useful
research-paper intake and browsing pattern.

The reusable asset is the ingest contract, not the hosted stack.

### What we verified

The repo currently uses:
- Next.js / React frontend
- Mantine UI
- Supabase SSR + client libraries
- Vercel analytics

The ingestion side is more interesting than the deployment side:
- scraper abstraction in `scripts/base.py`
- canonical CSV outputs: `venues.csv` and `papers.csv`

### Important schema caveat

The README describes venue rows in terms of `name, abbrev, year`, but the current
`scripts/base.py` implementation writes `venue["title"]`, `venue["abbrev"]`, `venue["year"]`.

We must normalize this in our own contract rather than inheriting the mismatch.

### Disposition

Borrow:
- scraper abstraction pattern
- CSV ingestion contract shape
- search / collection UX ideas

Do **not** inherit by default:
- Supabase-centric deployment assumptions
- hosted-stack assumptions
- analytics / telemetry defaults

This is **reference implementation only**.

## 4. Future training lane → `ServiceNow/Fast-LLM`

### Why this upstream matters

`Fast-LLM` is active, relevant, and technically credible for future distributed-training lanes.
It includes modern packaging, test configuration, and explicit cluster-launch examples.

### Disposition

Track it, but do not drag it into the immediate edge-capability critical path.

This belongs to a later lane focused on:
- distributed training
- cluster execution
- reproducible large-model evaluation and launch orchestration

## Immediate repo consequences

### `sociosphere` should own now

- capability schemas for `cap.edge.share` and `cap.edge.fingerprint`
- Cairn receipt schemas
- pin / lock policy for upstream tool revisions
- upstream tracking notes like this document

### Later extraction candidates

If `cap.edge.share` becomes a substantial hardened runtime rather than a thin wrapper,
we should graduate it out of `sociosphere` into a dedicated Linux/org repo while keeping
`sociosphere` as the canonical orchestrator / binder.

## Backlog

1. Pin one exact `KuroLabs/Airshare` baseline revision for Linux dev lane work
2. Build the Airshare hardening patchset backlog as a first-class tracked work item
3. Add deterministic provider-index hashing for `cdncheck`
4. Formalize our canonical `venues.csv` / `papers.csv` schema and resolve `name` vs `title`
5. Keep `Fast-LLM` on the training-lane watchlist, not the edge-capability path

## Status

Captured in repo. Not yet wired into docs index, lock files, or runner policy.
