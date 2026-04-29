# Complies with Standards — Multi-Domain Geospatial Intelligence

Status: Draft governance conformance

This governance repository consumes and enforces the SocioProphet multi-domain geospatial standards package.

## Standards consumed

- `SocioProphet/prophet-platform-standards/docs/standards/070-multidomain-geospatial-standards-alignment.md`
- `SocioProphet/prophet-platform-standards/registry/multidomain-geospatial-standards-map.v1.json`
- `SocioProphet/socioprophet-standards-storage/docs/standards/096-multidomain-geospatial-storage-contracts.md`
- `SocioProphet/socioprophet-standards-knowledge/docs/standards/080-multidomain-geospatial-knowledge-context.md`
- `SocioProphet/socioprophet-agent-standards/docs/standards/020-multidomain-geospatial-agent-runtime.md`

## Implementation responsibility

`SocioSphere` owns governance gates, standards compliance checks, source trust, data licensing checks, sensitive geospatial policy enforcement, redaction/masking gates, and cross-repo change-propagation rules.

## Required governance gates

- standards cross-reference check
- schema/fixture validator check
- source license and attribution check
- sensitive geospatial policy check
- defense/public-safety authorization check
- runtime evidence and replay check
- Lattice admission readiness check

## Promotion gate

No multi-domain geospatial implementation artifact should be promoted to stable unless SocioSphere can verify standards alignment across platform, storage, knowledge, and agent standards.
