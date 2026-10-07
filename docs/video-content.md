# Video Content API integration guide

`GET https://argolink.io/v1/videos/{request_id}/content` streams the finished MP4. It is the same address the [Video Status API](./video-status.md) returns as `video.url` once a job is `done`.

## Request

| | |
|---|---|
| Method | `GET` |
| URL | `https://argolink.io/v1/videos/{request_id}/content` |
| Header | `Authorization: Bearer YOUR_API_KEY` (same user as the job) |
| Optional header | `Range: bytes=START-` to resume a partial download |

## Response

`200` with `Content-Type: video/mp4`: one 24 fps H.264 video, up to 1080p, with an AAC stereo track (44.1 kHz) unless the job sent `generate_audio: false`. A `Range` request is answered with the requested bytes.

## Download with cURL

Wait for `done` first, then:

```bash
curl -fSL "https://argolink.io/v1/videos/$REQUEST_ID/content" \
  -H "Authorization: Bearer $API_KEY" -o result.mp4
```

`-f` matters: without it, a `409` error body would be written into `result.mp4`. If you would rather not poll, let curl retry until the file exists; this gives up after about ten minutes:

```bash
curl -fSL --retry 120 --retry-delay 5 --retry-all-errors \
  "https://argolink.io/v1/videos/$REQUEST_ID/content" \
  -H "Authorization: Bearer $API_KEY" -o result.mp4
```

## Resumable download in Python

```python
import os

import requests

API = "https://argolink.io/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['API_KEY']}"}


def download(request_id, path):
    """Stream the MP4 to path, continuing a partial file with a Range request."""
    have = os.path.getsize(path) if os.path.exists(path) else 0
    headers = dict(HEADERS, Range=f"bytes={have}-") if have else HEADERS
    with requests.get(f"{API}/videos/{request_id}/content", headers=headers, stream=True, timeout=600) as response:
        if response.status_code == 416:               # the file is already complete
            return path
        response.raise_for_status()
        mode = "ab" if response.status_code == 206 else "wb"
        with open(path, mode) as handle:
            for chunk in response.iter_content(chunk_size=1 << 20):
                handle.write(chunk)
    return path
```

## Error codes

| HTTP | `error.code` | Meaning | What to do |
|---|---|---|---|
| 401 | — | missing or invalid key | check the key |
| 404 | `video_request_not_found` | unknown ID, or another user's job | use the creator's key |
| 409 | `job_video_not_ready` | the job is still `pending` | request the same URL again shortly |
| 424 | `job_failed` | the job failed | read `error` on the [status](./video-status.md) |
