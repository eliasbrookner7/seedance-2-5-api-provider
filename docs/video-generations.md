# Video Generations API integration guide

`POST https://argolink.io/v1/videos/generations` starts a Seedance 2.5 job. It answers at once with HTTP `202` and a `request_id`; the video itself is produced asynchronously and fetched with the [Video Status](./video-status.md) and [Video Content](./video-content.md) APIs.

## Request headers

| Header | Value |
|---|---|
| `Authorization` | `Bearer YOUR_API_KEY` |
| `Content-Type` | `application/json` |

The whole JSON body must stay under 1 MiB, and every media field carries a public `https://` URL. Base64 data, multipart bodies and file IDs are rejected; upload local files with the [Media Uploads API](./media-uploads.md) first.

## Body fields

**Core**

| Field | Type | Default | Rule |
|---|---|---|---|
| `model` | string | — | `seedance-2.5` |
| `prompt` | string | — | required in every mode; up to 40,000 bytes of UTF-8 |
| `duration` | integer | `5` | 4–30 whole seconds; not sent with an edit |
| `resolution` | string | `720p` | `480p`, `720p` or `1080p` |
| `aspect_ratio` | string | `16:9` | `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`; frame requests take `adaptive` only |
| `size` | string | — | pixels instead of resolution + ratio, e.g. `1920x1080` (1080p, 16:9) |
| `generate_audio` | boolean | `true` | `false` renders without a soundtrack |
| `n` | integer | `1` | only `1` |

**Frames**: `start_image` `{url}` alone makes a first-frame video; adding `end_image` `{url}` makes the model fill the motion between the two. Neither can be combined with a reference list.

**References**: `reference_images` (up to 30), `reference_videos` (up to 10, 2–30 s each, 30 s together) and `reference_audios` (up to 10, same lengths), 50 assets in total, as arrays of `{url}`. Name them in the prompt as `@Image 1`, `@Video 1`, `@Audio 1`; the number is the 1-based position in its own array. Audio may be the only reference.

**Edit**: `omni_reference_task_type: "edit"` with exactly one entry in `reference_videos` (4–30 s) rewrites that clip. The result keeps its length and ratio, so `duration` and `aspect_ratio` are left out; images, audio and frames cannot be added.

Not supported: `seed`, `watermark: true`, and the `extend` task type.

## Examples by workflow

### Text to video (cURL)

```bash
curl -sS https://argolink.io/v1/videos/generations \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "seedance-2.5",
    "prompt": "A cyclist races down an alpine pass, the camera tracks alongside at road level",
    "duration": 8,
    "resolution": "1080p",
    "aspect_ratio": "21:9"
  }'
```

### Text to video (Python)

```python
import os

import requests

session = requests.Session()
session.headers["Authorization"] = f"Bearer {os.environ['API_KEY']}"

response = session.post(
    "https://argolink.io/v1/videos/generations",
    json={
        "model": "seedance-2.5",
        "prompt": "A cyclist races down an alpine pass, the camera tracks alongside at road level",
        "duration": 8,
        "resolution": "1080p",
        "aspect_ratio": "21:9",
    },
    timeout=60,
)
response.raise_for_status()          # HTTP 202
print(response.json()["request_id"])
```

### First frame and first + last frame

```json
{
  "model": "seedance-2.5",
  "prompt": "The rider looks over her shoulder and accelerates out of the frame",
  "duration": 5,
  "resolution": "720p",
  "aspect_ratio": "adaptive",
  "start_image": {"url": "https://example.com/rider.jpg"},
  "end_image": {"url": "https://example.com/empty-road.jpg"}
}
```

Drop `end_image` for a first-frame-only video. The output takes the ratio closest to the first frame.

### Multimodal reference

```json
{
  "model": "seedance-2.5",
  "prompt": "The presenter in @Image 1 explains the product in @Image 2, gesturing like @Video 1, voice from @Audio 1",
  "duration": 12,
  "resolution": "720p",
  "aspect_ratio": "9:16",
  "reference_images": [{"url": "https://example.com/presenter.png"}, {"url": "https://example.com/product.png"}],
  "reference_videos": [{"url": "https://example.com/gestures.mp4"}],
  "reference_audios": [{"url": "https://example.com/voiceover.mp3"}]
}
```

A 6.5-second `gestures.mp4` adds 6 billed seconds, so this job bills 18 seconds: 18 × $0.196 = $3.528.

### Edit an existing video

```json
{
  "model": "seedance-2.5",
  "omni_reference_task_type": "edit",
  "prompt": "Change the season to autumn with falling leaves, keep the people and the camera move",
  "resolution": "1080p",
  "reference_videos": [{"url": "https://example.com/park-10s.mp4"}]
}
```

The edited clip bills as output and as a reference: a 10-second source at 1080p is 20 × $0.483 = $9.66.

## Response

```json
{"request_id": "5b0e2f8a-3c71-4d9e-a2b6-90f1c4d7e815"}
```

Store `request_id` before anything else: it is the only handle for the status, the download and the billing record, and only keys of the user who created the job can read it.

## Field names from other APIs

Bodies written for fal or OpenRouter can be posted unchanged; give each input one name.

| Field here | Also accepted |
|---|---|
| `start_image` | `image_url` (a URL string), or a `frame_images` item with `"frame_type": "first_frame"` |
| `end_image` | `end_image_url`, or a `frame_images` item with `"frame_type": "last_frame"` |
| `reference_images` / `_videos` / `_audios` | `image_urls` / `video_urls` / `audio_urls`, or `input_references` items of type `image_url` / `video_url` / `audio_url` |
| `duration`, `aspect_ratio` | `seconds`, `ratio` |
| `resolution` + `aspect_ratio` | `size` |

## Error codes

| HTTP | `error.code` | Meaning | Charged |
|---|---|---|---|
| 400 | `field_invalid`, `json_invalid` | malformed request: a wrong type, neither prompt nor media, `end_image` alone, frames mixed with references, a non-HTTPS URL | no |
| 400 | `request_unsupported` | the model does not accept the combination; `message` says which (resolution, duration, ratio, `seed`, asset count, a mention past the end of a list) | no |
| 401 | — | missing or invalid key | no |
| 402 / 403 | — | insufficient balance, or the key's group has no video permission | no |
| 429 | — | concurrency or rate limit (up to 50 Seedance 2.5 jobs run at once per account) | no |
| 503 | `no_capacity` | no capacity now; retry after the `Retry-After` header | no |
| 503 | — | temporary outage; retry later | no |

Every error body is `{"error": {"type": "…", "code": "…", "param": "…", "message": "…"}}`. `param` names the field at fault and `message` can be shown to a user.
