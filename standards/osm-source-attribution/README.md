# OpenStreetMap Source Attribution Standard

Status: v0 governance standard

## Purpose

This standard defines publication-safety and attribution requirements for OpenStreetMap-derived artifacts used by GAIA, Prophet Platform, Sherlock Search, Lattice Forge, Lampstand, and SocioSphere.

## Rule

No public or user-facing OSM-derived artifact is release-ready unless it preserves:

- OSM source identity where available: node, way, relation;
- OSM source refs;
- attribution text;
- license refs;
- provenance refs;
- advisory/safety status for route outputs.

## Required checks

- OSMFeatureBinding has `osm_ref`, `attribution`, and `provenance.source_refs`.
- MapTileLayerManifest has `attribution.attribution_text`, license refs, and source refs.
- OSMRouteGraphManifest has `safety_status=advisory` unless a route validation/safety case exists.
- Sherlock OSM-derived records include OSM spatial refs and provenance refs.
- Lattice RuntimeAssets for OSM runtimes are not allowed until runtime admission criteria are satisfied.

## Non-goals

- This standard does not interpret OSM legal obligations.
- This standard does not replace legal review.
- This standard does not grant permission to make safety-critical route claims.
