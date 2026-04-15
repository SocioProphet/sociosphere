## Local‑First Fabric for Fog/Hybrid Multi‑Mesh Workspaces
**Self‑contained research + design doc (TopoLVM + FabricFS + Hyper* + Drive/rsync/S3 + Quorum/Policy + Tool ABI)**
**Date:** 2026‑03‑05 (America/New_York)

# 0) The primitives we’re building

We’re going to name the nouns precisely, because fuzzy nouns become outages.

### Data primitives
- **DatasetRef**: logical dataset identity.
- **VolumeRef**: a dataset versioned surface (RW head or RO release snapshot).
- **MountRef**: a concrete mount instance on a node (path + capabilities + fingerprint).
- **ObjectRef**: content-addressed object (e.g., `sha256`) + metadata.
- **ManifestRef**: immutable manifest root describing the current tree/object set.
- **IndexRef**: retrieval artifacts bound to a manifest (chunks, vectors, keyword postings).
- **IndexPack**: portable bundle of IndexRef for replication/import.

### Distribution primitives
- **DriveRef**: Hyperdrive dataset handle.
- **TopicRef**: discovery/rendezvous handle (private/lan/public policy governed).
- **Journal**: append-only signed event log (operations + provenance + policy decisions).

### Control primitives
- **Cell**: admin/trust boundary (AFS-inspired).
- **PolicyBundle**: versioned policy set + profiles.
- **QuorumAction**: proposal/approval/commit objects for high-impact actions.
- **ToolRef**: portable tool descriptor + schemas + capability requirements.

### 0.2 Storage primitives (mounts)
A “mount” is not a path — it’s a **capability + policy + lifecycle**.

- **MountSpec** (desired state, YAML)
- **MountHandle** (resolved instance: node, path/PVC, capacity, rw/ro)
- **MountManifest** (file graph, hashes, metadata)
- **MountIndexBundle** (keyword + vector + chunk refs)
- **MountPolicyBundle** (retention, quotas, egress, redaction, adversary mode)
- **MountCapability** (scoped grants: read/query/write/index/export)

### 0.3 Index primitives
- **ChunkSet** (stable chunk ids → byte ranges)
- **EmbeddingSet** (vectors + metadata)
- **KeywordIndex** (lexical)
- **IndexFeed** (append-only deltas)

### 0.4 Distribution primitives (Hyper ecosystem)
- **Hypercore feed** = secure append‑only log ([github.com](https://github.com/holepunchto/hypercore))
- **Hyperswarm** = DHT-based peer discovery for Hypercore replication ([hypercore-protocol.github.io](https://hypercore-protocol.github.io/new-website/guides/modules/hyperswarm/))
- **Hyperdrive** = P2P filesystem; `drive.discoveryKey` can be used as the topic to seed via Hyperswarm. ([github.com](https://github.com/holepunchto/hyperdrive/blob/main/README.md))

### 0.5 Threat posture primitive
We explicitly model a Briar-like assumption: hostile networks + intermittent connectivity + offline operation. Briar synchronizes directly device-to-device; when Internet is down it can sync via Bluetooth/Wi‑Fi/memory cards; when Internet is up it can sync via Tor. ([briarproject.org](https://briarproject.org/how-it-works/))
We don’t have to copy Briar’s stack, but we copy the *posture*.

---

# 1) Highest‑impact improvements for a local‑first hybrid/fog multi‑mesh design

If we only do five things “right,” these are the five:

### 1) Make canonical storage *ours* and content-addressed
- Canonical bytes live in a **local-first object store** (S3-compatible, often MinIO), backed by **TopoLVM** volumes in K8s cluster deployments.
- This immediately eliminates “vendor quota” as a system-of-record failure mode, and makes replication and dedupe straightforward.

### 2) Attach indexing to mounting as a first-class handshake
Mount/register must return an **IndexRef** immediately (even if warming). This avoids “files are mounted but not searchable” limbo and makes integrations deterministic.

### 3) Introduce a cluster-style terminal filesystem (AFS-inspired) for humans
A community doesn’t operate a cluster via clicky menus; they operate it via a **shared namespace** (`/home`, `/proj`, `/scratch`) and a small set of **filesystem commands** (`fs examine`, `fs listquota`, `fs setacl`, …).

AFS mount points appear as directories; crossing them can transparently move you into another volume; `fs examine` surfaces mount/quota details. ([cs.unc.edu](https://cs.unc.edu/resources/andrew-file-system-afs/?utm_source=chatgpt.com))
AFS ACLs are directory-scoped, inherited by new directories, and moving files changes effective permissions by directory context. ([computing.help.inf.ed.ac.uk](https://computing.help.inf.ed.ac.uk/afs-acls?utm_source=chatgpt.com))
AFS “lookup” permission is foundational for directory traversal. ([uit.stanford.edu](https://uit.stanford.edu/service/afs/learningmore/permissions?utm_source=chatgpt.com))

### 4) Treat intermittent/adversarial connectivity as normal
We assume Briar-grade conditions: no central server required, direct device sync, and alternative transports when internet is down (Bluetooth/Wi‑Fi/removable media) and privacy-preserving transports when internet is up (Tor). ([briarproject.org](https://briarproject.org/how-it-works/?utm_source=chatgpt.com))
We borrow the *delay‑tolerant secure channel* mindset; Briar’s BTP is explicitly intended for delay‑tolerant networks. ([code.briarproject.org](https://code.briarproject.org/briar/briar-spec/-/blob/master/protocols/BTP.md?utm_source=chatgpt.com))

### 5) Governance is a product feature: quorum + policy library + playbooks
High-impact actions (enabling WAN egress, publishing topics publicly, key rotations, destructive deletions) must be **multi-party approved** and **auditable**.

---

## 2) Requirements and threat model
### Operational requirements
- Local-first: usable with **zero cloud access**.
- Hybrid/fog: multiple sites, intermittent links, mixed hardware, mixed trust domains.
- Multi‑mesh: multiple transports (LAN, WAN, Tor, offline media; plus P2P rendezvous).
- Mount TopoLVM volumes into workspaces and **register an index** as part of the handshake.
- Integrate with: **Google Drive API**, **rsync**, **MinIO/S3**, **Hypercore/Hyperdrive/Hyperswarm**.
- Add tools/capabilities in a portable way (vendor-neutral Tool ABI).
- Adversarial networks: censorship, surveillance, partitions, replay attempts.
- Metadata minimization: avoid leaking filenames, directory structure, or topics when in high-threat mode.
- Explicit egress control: LLM providers only see minimal chunks necessary.
- Strong governance and auditability.

---

## 3) Primitive inventory (canonical vocabulary)
We’ll use these terms consistently across all diagrams and examples:

### Data primitives
- **DatasetRef**: logical dataset identity.
- **VolumeRef**: a dataset versioned surface (RW head or RO release snapshot).
- **MountRef**: a concrete mount instance on a node (path + capabilities + fingerprint).
- **ObjectRef**: content-addressed object (e.g., `sha256`) + metadata.
- **ManifestRef**: immutable manifest root describing the current tree/object set.
- **IndexRef**: retrieval artifacts bound to a manifest (chunks, vectors, keyword postings).
- **IndexPack**: portable bundle of IndexRef for replication/import.

### Distribution primitives
- **DriveRef**: Hyperdrive dataset handle.
- **TopicRef**: discovery/rendezvous handle (private/lan/public policy governed).
- **Journal**: append-only signed event log (operations + provenance + policy decisions).

### Control primitives
- **Cell**: admin/trust boundary (AFS-inspired).
- **PolicyBundle**: versioned policy set + profiles.
- **QuorumAction**: proposal/approval/commit objects for high-impact actions.
- **ToolRef**: portable tool descriptor + schemas + capability requirements.

### 0.2 Storage primitives (mounts)
A “mount” is not a path — it’s a **capability + policy + lifecycle**.

- **MountSpec** (desired state, YAML)
- **MountHandle** (resolved instance: node, path/PVC, capacity, rw/ro)
- **MountManifest** (file graph, hashes, metadata)
- **MountIndexBundle** (keyword + vector + chunk refs)
- **MountPolicyBundle** (retention, quotas, egress, redaction, adversary mode)
- **MountCapability** (scoped grants: read/query/write/index/export)

---