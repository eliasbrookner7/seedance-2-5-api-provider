# Media Uploads API integration guide

Generation requests only carry HTTPS URLs. When an image, clip or audio file is on your disk, `POST https://argolink.io/v1/media/uploads` issues an upload ticket: you `PUT` the bytes straight to object storage and pass the returned `media_url` to the [Video Generations API](./video-generations.md). Tickets are free and create no job.

## Step 1: ask for a ticket

| Field | Type | Rule |
|---|---|---|
| `model` | string | `seedance-2.5` |
| `type` | string | `image`, `video` or `audio` |
| `content_type` | string | the MIME type you will `PUT` with (see below) |
| `size_bytes` | integer | must equal the real file size |

The response carries:

| Field | Meaning |
|---|---|
| `upload_url` | presigned URL; `PUT` within 15 minutes with exactly the declared `Content-Type` |
| `media_url` | the address to put in `start_image`, `end_image` or a reference list; readable for 7 days |
| `upload_expires_at`, `expires_at` | when each of the two stops working |

## Step 2: PUT the bytes

The `PUT` goes to the storage host, not to the API, so it takes no `Authorization` header; only `Content-Type`.

```bash
FILE=./intro.mov
SIZE=$(wc -c < "$FILE" | tr -d ' ')     # portable; or stat -f%z (macOS) / stat -c%s (Linux)

TICKET=$(curl -fsS https://argolink.io/v1/media/uploads \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"seedance-2.5\",\"type\":\"video\",\"content_type\":\"video/quicktime\",\"size_bytes\":$SIZE}")

curl -fsS -X PUT "$(jq -r .upload_url <<<"$TICKET")" \
  -H "Content-Type: video/quicktime" --data-binary @"$FILE"

MEDIA_URL=$(jq -r .media_url <<<"$TICKET")
echo "$MEDIA_URL"
```

## Step 3: use the media_url

```json
{
  "model": "seedance-2.5",
  "prompt": "The host from @Video 1 walks into a sunlit studio and waves",
  "reference_videos": [{"url": "MEDIA_URL"}]
}
```

## Python helper

```python
import os

import requests

API = "https://argolink.io/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['API_KEY']}"}

# The formats Seedance 2.5 reads, with the MIME types the ticket expects
# (mimetypes.guess_type says audio/x-wav for .wav, which is not on the ticket's list).
TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".mp4": "video/mp4", ".mov": "video/quicktime",
    ".mp3": "audio/mpeg", ".wav": "audio/wav",
}


def upload(path):
    """Upload a local image, video or audio file and return its media_url."""
    content_type = TYPES.get(os.path.splitext(path)[1].lower())
    if content_type is None:
        raise ValueError(f"{path}: Seedance 2.5 reads JPEG, PNG, MP4, MOV, MP3 and WAV")
    kind = content_type.split("/")[0]
    ticket = requests.post(f"{API}/media/uploads", headers=HEADERS, timeout=30, json={
        "model": "seedance-2.5",
        "type": kind,
        "content_type": content_type,
        "size_bytes": os.path.getsize(path),
    })
    ticket.raise_for_status()
    with open(path, "rb") as handle:
        put = requests.put(ticket.json()["upload_url"], data=handle,
                           headers={"Content-Type": content_type}, timeout=600)
    put.raise_for_status()
    return ticket.json()["media_url"]
```

## Types and limits

A ticket accepts more types than Seedance 2.5 reads; the job checks the stricter Seedance limits.

| `type` | Ticket `content_type` | Ticket max | Seedance 2.5 reads |
|---|---|---|---|
| `image` | `image/jpeg`, `image/png`, `image/webp` | 20 MiB | JPEG or PNG ≤ 20 MiB, 300–6000 px per side, width/height 0.4–2.5 |
| `video` | `video/mp4`, `video/quicktime`, `video/webm` | 500 MiB | MP4 or MOV ≤ 100 MiB, 2–30 s (4–30 s for an edit), 24–60 fps, 300–6000 px per side |
| `audio` | `audio/mpeg`, `audio/wav`, `audio/mp4`, `audio/aac` | 20 MiB | WAV or MP3 ≤ 15 MB, 2–30 s |

Counts and media types are checked when the job is submitted. Clip lengths are checked after upload, before generation starts: a clip out of range fails the job with `invalid_input`, and nothing is charged.
