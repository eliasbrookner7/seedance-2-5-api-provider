# seedance-2.5 API

A focused Argolink guide for seedance-2.5 requests. The public examples use only Argolink hosts and environment-based credentials.

[Open the Argolink model page →](https://argolink.io/gh-seedance-2-5-api-provider)

## What is covered

- a single Argolink request lifecycle;
- model fields, media references, and validation boundaries;
- bounded polling, terminal errors, and safe retries;
- cURL examples that can be adapted to a typed client.

See [`docs/video-api-contract.md`](./docs/video-api-contract.md) for the complete submit → poll → download flow.

## Public contract boundary

This repository is an integration aid, not an authority for prices or availability. Read the linked Argolink model or API page immediately before deployment. Runtime access uses `ARGOLINK_API_KEY`; do not copy a key into source, issues, screenshots, or generated artifacts.

## Repository map

- [`ARGOLINK.md`](./ARGOLINK.md): scope and public boundary.
- [`docs/`](./docs): durable request and validation notes.
- [`examples/`](./examples): runnable, credential-free examples.
- [`argolink/`](./argolink): Argolink-specific mapping and review checklist.
- [`ARGOLINK_LINKS.md`](./ARGOLINK_LINKS.md): tracked landing link.
