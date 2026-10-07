# Video Status API integration guide

`GET https://argolink.io/v1/videos/{request_id}` returns the current state of a job created by the [Video Generations API](./video-generations.md). Poll it until the status leaves `pending`.

## Request

| | |
|---|---|
| Method | `GET` |
| URL | `https://argolink.io/v1/videos/{request_id}` |
| Header | `Authorization: Bearer YOUR_API_KEY`, a key of the same user who created the job |
| Cadence | every 10–15 seconds |

A key of a different user, or an ID that does not exist, gets `404` with `video_request_not_found`.

## Statuses

| `status` | Meaning | Fields present |
|---|---|---|
| `pending` | queued or generating | `progress` (0–99), `estimated_seconds_remaining` once a forecast exists |
| `done` | the MP4 is ready | `progress: 100`, `video.url`, `video.duration`, `usage` |
| `failed` | no video; not charged | `error.code`, `error.message`, `error.retryable`, sometimes `error.field` |
| `expired` | no video; not charged | — |

`progress` and the ETA are worked out from the forecast of the job's queue and generation time. Until there is a forecast, `progress` is `0`; a job that runs past its forecast holds at `99` until it finishes. For a 4–10 second clip the whole run usually takes 2–5 minutes.

## Response examples

Pending:

```json
{
  "request_id": "5b0e2f8a-3c71-4d9e-a2b6-90f1c4d7e815",
  "status": "pending",
  "model": "seedance-2.5",
  "created_at": 1791374400,
  "progress": 63,
  "estimated_seconds_remaining": 54
}
```

Done:

```json
{
  "request_id": "5b0e2f8a-3c71-4d9e-a2b6-90f1c4d7e815",
  "status": "done",
  "model": "seedance-2.5",
  "created_at": 1791374400,
  "progress": 100,
  "video": {"duration": 12, "url": "https://argolink.io/v1/videos/5b0e2f8a-3c71-4d9e-a2b6-90f1c4d7e815/content"},
  "usage": {"output_seconds": 12, "reference_video_seconds": 6, "billed_seconds": 18}
}
```

`usage.billed_seconds` is what the job is charged for, multiplied by the per-second rate of its resolution. The charge is made once, when `done` is first observed.

Failed:

```json
{
  "request_id": "0c9d7b3e-1f24-4a8b-b6e0-58d2a7c3f901",
  "status": "failed",
  "model": "seedance-2.5",
  "error": {
    "code": "invalid_input",
    "message": "aspect_ratio must be adaptive for first-frame, first-last-frame, and edit requests. Set aspect_ratio to adaptive and submit again.",
    "retryable": false,
    "field": "start_image"
  }
}
```

## Failure codes

| `error.code` | `retryable` | What happened | What to do |
|---|---|---|---|
| `invalid_input` | false | an input cannot be used, e.g. a reference clip outside 2–30 s or a fixed ratio on a frame request | fix `error.field` and submit again |
| `content_policy_violation` | false | content review refused an input (named in `field`) or the result | change the input |
| `copyright_violation` | true or false | true: the generated result, such as its audio, was flagged; false: an input was | true: submit again or reword; false: replace the input |
| `generation_failed` | true or false | generation failed | resubmit only when `retryable` is true |
| `generation_timeout` | false | generation started but had no result after 24 hours | submit a new job |
| `capacity_unavailable` | true | nothing could take the job within 10 minutes of queueing | submit again later |
| `internal_error` | true | the service failed before generation started | submit again |
| `cancelled` | false | the job was cancelled | — |

`retryable: true` means the failure consumed no generation and the same request can be sent again safely. Failed and expired jobs are never charged.

## Polling in Python

```python
import os
import time

import requests

API = "https://argolink.io/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['API_KEY']}"}


def wait_for_video(request_id, interval=12, give_up_after=1800):
    """Return the finished job; raise with the error object if it failed or expired."""
    deadline = time.monotonic() + give_up_after
    while time.monotonic() < deadline:
        response = requests.get(f"{API}/videos/{request_id}", headers=HEADERS, timeout=30)
        if response.status_code in (429, 503):        # not an answer about the job: back off
            time.sleep(int(response.headers.get("Retry-After", interval)))
            continue
        response.raise_for_status()
        job = response.json()
        if job["status"] == "done":
            return job
        if job["status"] in ("failed", "expired"):
            raise RuntimeError(job.get("error") or job["status"])
        time.sleep(interval)
    raise TimeoutError(f"{request_id} is still pending; poll again later, the job keeps running")
```

## Error codes

| HTTP | `error.code` | Meaning |
|---|---|---|
| 401 | — | missing or invalid key |
| 404 | `video_request_not_found` | unknown `request_id`, or a key of another user |
| 429 | — | rate limit; slow down |
| 503 | — | temporary; retry |
