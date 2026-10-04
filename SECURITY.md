# Security

- Keep `ARGOLINK_API_KEY` in the process environment or a secret manager.
- Redact authorization headers and upload URLs from logs.
- Validate media type, byte size, and duration before submission.
- Use the same account key for a job's status and content requests.
- Report a suspected key leak by revoking the key first, then preserving only redacted request IDs for diagnosis.
