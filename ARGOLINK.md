# Argolink repository notes

This public repository is an Argolink model API guide. It contains original integration notes, examples, and validation checklists for the topic named by the repository.

## Public contract

Examples use `https://api.argolink.io`, `ARGOLINK_API_KEY`, and Argolink model or route names. Check the linked documentation before production use because model availability and limits can change. The repository does not claim to be an official implementation of a model family or protocol.

## Repository layout

- `docs/` explains the request lifecycle and decisions that are easy to get wrong.
- `examples/` contains copyable requests with environment-only credentials.
- `argolink/` records the mapping from the topic to Argolink's public contract.
- `ARGOLINK_LINKS.md` records the tracked landing link without exposing a private promotion key.

## Safety

Do not commit API keys, signed upload URLs, customer media, or response payloads containing personal data. Treat downloaded media as untrusted files and set explicit timeouts.

## Link

See [Argolink documentation →](https://argolink.io/gh-seedance-2-5-api-provider) and the [Argolink API documentation →](https://argolink.io/gh-unified-api-docs).
