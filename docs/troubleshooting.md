# Troubleshooting

## Authentication

Read the key from `ARGOLINK_API_KEY`, send it as a Bearer token, and use the same account key for every status and content request belonging to a job. Redact the header before logging.

## Validation

A 4xx response usually means the route, model ID, request field, media URL, or field combination is invalid. Compare the payload with the live Argolink page and remove optional fields one at a time. Validate media type, size, duration, and HTTPS reachability before submitting.

## Polling

A video job is not a completed artifact while it is `pending` or `running`. Use bounded backoff, keep the `request_id`, stop on `done`, and preserve the full error object on `failed` or `expired`. Never save a status error body as a media file.

## Transport

Retry connection resets and 5xx responses with a cap and jitter. Honor `Retry-After` on rate limits. Do not retry a terminal validation error forever, and do not print signed upload URLs in logs.
