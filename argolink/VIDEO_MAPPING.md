# Argolink seedance-2.5 mapping

This directory keeps the topic-specific vocabulary while routing every public example through Argolink's asynchronous video contract. The stable boundary is `POST /v1/videos/generations`, followed by status and content requests using the same `request_id`.

## Review checklist

- [ ] `ARGOLINK_API_KEY` is injected at runtime.
- [ ] The model page is checked before optional fields are sent.
- [ ] Reference URLs are HTTPS and media limits are validated.
- [ ] Polling is bounded and terminal errors are preserved.
- [ ] Downloaded content is treated as untrusted input.
