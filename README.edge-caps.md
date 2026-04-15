# Edge Capabilities (Draft v0.1)

This directory introduces two mesh-edge capabilities designed to be wrapped by TriTRPC and logged as Cairn receipts.

## cap.edge.fingerprint@0.1 (cdncheck)
- Purpose: Identify CDN / Cloud / WAF properties for IP/DNS inputs.
- Output: JSONL records; one record per input; also emits a `cairn.edge.fingerprint@0.1` receipt.

## cap.edge.share@0.1 (airshare)
- Purpose: Local network sharing (files + clipboard) with mDNS discovery.
- Output: Emits `cairn.edge.share.transfer@0.1` receipts for send/receive.

## Next
- Add shim CLIs in `caps/edge-fingerprint/` and `caps/edge-share/` that normalize outputs and collect evidence hashes.
- Add TriTRPC handshake envelope and TOFU+receipt flow.
