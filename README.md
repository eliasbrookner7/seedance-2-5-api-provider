# Seedance 2.5 API provider — $0.0874/s at 480p, 15% under BytePlus

**ByteDance Seedance 2.5 is live on [ArgoLink](https://argolink.io/gh-seedance-2-5-api-provider)**: $0.0874/s at 480p, $0.196/s at 720p and $0.483/s at 1080p, 15% below the BytePlus ModelArk list price. Text, images, video and audio go in; a 4–30 second MP4 with generated sound comes out, through four REST endpoints that each have an integration guide in [`docs/`](./docs).

[Get an API key](https://argolink.io/app/keys) · [Model page](https://argolink.io/en/models/seedance-2.5) · [Integration guides](#apis-and-guides) · [Error codes](#error-codes) · [Migrating from BytePlus](#migrating-from-byteplus-modelark)

<sub>Last checked: 2026-10-07 against the provider's model page and API guide, and BytePlus's pricing page and Seedance 2.5 guide.</sub>

## Overview

Seedance 2.5 is ByteDance's video model for clips of up to 30 seconds, with a soundtrack the model writes itself and up to 50 reference images, videos and audio clips per request. It also rewrites video you already have. ByteDance sells it on BytePlus ModelArk as `dreamina-seedance-2-5-260628`; gateways resell access under their own keys and request formats.

This repository is the integration guide for one such provider: how to get access, what each endpoint takes and returns, what every error means, and how a BytePlus request maps onto this API.

## Provider or BytePlus direct?

Both run the same model. The differences are in price, limits and request shape:

| | BytePlus ModelArk (official) | ArgoLink |
|---|---|---|
| Model ID | `dreamina-seedance-2-5-260628` | `seedance-2.5` |
| 720p, no video input | $0.2311/s ($10.70 per million tokens) | $0.196/s |
| With a reference video | $6.40 per million tokens over input + output seconds, with a minimum token charge | $0.196 per output + reference second |
| Billing unit | tokens, which grow with frame size and length | whole seconds |
| Tasks at once | 3 (individual account), 10 (enterprise) | 50 per account |
| Request format | a `content` array of items with roles | flat fields; fal and OpenRouter field names accepted |
| Image input | URL or Base64 | HTTPS URL; free upload tickets for local files |
| Model-chosen length (`duration: -1`) | yes | no; an edit keeps its source's length |
| `seed`, draft mode, video extension | yes | no |
| Failed jobs | not charged | not charged |

<sub>BytePlus: [pricing](https://docs.byteplus.com/en/docs/modelark/model-pricing) and [Seedance 2.5 guide](https://docs.byteplus.com/en/docs/modelark/seedance-2-5), read 2026-10-07. With a reference video, BytePlus's lower token rate can make a video-heavy job cheaper there than here; compare with your own clip lengths.</sub>

## Getting access

1. Create an account at [argolink.io](https://argolink.io) with email or Google.
2. Top up in the console wallet. Payment runs through PayPal, and Visa, Mastercard and Amex cards work without a PayPal account. The minimum is $1.
3. Create a key on the [API Keys page](https://argolink.io/app/keys).
4. Send requests to `https://argolink.io/v1` with `Authorization: Bearer YOUR_API_KEY`.

There is no separate application per model. `GET https://argolink.io/v1/models` lists the whole catalog without a key; a key whose group may not use video models gets `402`/`403` on submit.

## Quick start

```bash
export API_KEY=your-key

# submit: HTTP 202 with a request_id
ID=$(curl -fsS https://argolink.io/v1/videos/generations \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"seedance-2.5","prompt":"A street musician plays violin under a bridge as the rain stops","duration":6,"resolution":"720p"}' \
  | jq -r .request_id)

# poll every 12 s until the status is no longer "pending"
until [ "$(curl -fsS https://argolink.io/v1/videos/$ID -H "Authorization: Bearer $API_KEY" | jq -r .status)" != pending ]; do
  sleep 12
done

# download (fails cleanly with -f if the job did not finish as done)
curl -fSL https://argolink.io/v1/videos/$ID/content -H "Authorization: Bearer $API_KEY" -o violin.mp4
```

## Models

All four Seedance models on this provider share the endpoint and the request shape; this repository documents `seedance-2.5`.

| Model | Generation | Clip length | Resolution | References | From |
|---|---|---|---|---|---|
| `seedance-2.5` | 2.5 | 4–30 s | 480p · 720p · 1080p | 30 images, 10 videos, 10 audio | $0.0874/s |
| `seedance-2.0` | 2.0 | 4–15 s | 480p · 720p · 1080p · 4K | 9 images, 3 videos, 3 audio | $0.053/s |
| `seedance-2.0-fast` | 2.0 Fast | 4–15 s | 480p · 720p | 9 images, 3 videos, 3 audio | $0.042/s |
| `seedance-2.0-mini` | 2.0 Mini | 4–15 s | 480p · 720p | 9 images, 3 videos, 3 audio | $0.026/s |

Only `seedance-2.5` edits existing video and accepts audio as the only reference.

## APIs and guides

| API | Method and path | Integration guide |
|---|---|---|
| Media Uploads | `POST /v1/media/uploads` | [media-uploads.md](./docs/media-uploads.md): ticket, `PUT`, limits per file type |
| Video Generations | `POST /v1/videos/generations` | [video-generations.md](./docs/video-generations.md): every field, five workflows, alias names |
| Video Status | `GET /v1/videos/{request_id}` | [video-status.md](./docs/video-status.md): statuses, progress, failure codes, a polling function |
| Video Content | `GET /v1/videos/{request_id}/content` | [video-content.md](./docs/video-content.md): streaming and resumable downloads |
| Models | `GET /v1/models` | public, OpenAI-shaped list; no key needed |

## Pricing

Price per second of output for a request without video input:

| Provider | 480p | 720p | 1080p | 5 s at 480p |
|---|---:|---:|---:|---:|
| **[ArgoLink](https://argolink.io/en/models/seedance-2.5)** | **$0.0874** | **$0.196** | **$0.483** | **$0.44** |
| [BytePlus ModelArk](https://docs.byteplus.com/en/docs/modelark/model-pricing) (official) | $0.1028 | $0.2311 | $0.5686 | $0.51 |
| [OpenRouter](https://openrouter.ai/bytedance/seedance-2.5), at BytePlus rates + 5.5% card fee on credits | $0.1028 | $0.2311 | — | $0.51 + fee |
| [fal.ai](https://fal.ai/models/bytedance/seedance-2.5/text-to-video) | $0.2205 | $0.4730 | $1.164 | $1.10 |

<sub>Read on 2026-10-07. BytePlus's own example prices a 5-second 480p clip at $0.514. OpenRouter's model FAQ lists 480p and 720p; its fee is in its [FAQ](https://openrouter.ai/docs/faq).</sub>

How a job is billed here:

- billed seconds = output seconds (rounded) + reference-video seconds (fractions dropped), times the rate of the resolution
- reference images, reference audio and uploads are free
- an edit counts the edited clip twice, as output and as reference: a 10 s edit at 1080p bills 20 s, $9.66
- a job without `duration` runs and bills 5 seconds
- failed and expired jobs are not charged; the charge happens once, when the job first reads `done`

## Error codes

Errors are `{"error": {"type": "…", "code": "…", "param": "…", "message": "…"}}` with a stable `code`.

| HTTP | Code | Where | Meaning |
|---|---|---|---|
| 400 | `field_invalid`, `json_invalid` | submit | malformed request |
| 400 | `request_unsupported` | submit | the model does not accept this combination (resolution, duration, ratio, `seed`, asset counts) |
| 401 | — | all | missing or invalid key |
| 402 / 403 | — | submit | insufficient balance, or no video permission on the key |
| 404 | `video_request_not_found` | status, content | unknown ID or another user's job |
| 409 | `job_video_not_ready` | content | still pending |
| 424 | `job_failed` | content | the job failed; read its status |
| 429 | — | all | concurrency or rate limit |
| 503 | `no_capacity` | submit | no capacity now; retry after `Retry-After` |

Jobs that were accepted but failed report `invalid_input`, `content_policy_violation`, `copyright_violation`, `generation_failed`, `generation_timeout`, `capacity_unavailable`, `internal_error` or `cancelled`, each with a `retryable` flag. The table in [video-status.md](./docs/video-status.md#failure-codes) says what to do for each.

## Migrating from BytePlus ModelArk

BytePlus takes a `content` array whose items carry a `role`; this API takes one field per role. The model behaves the same; only the envelope changes.

| BytePlus ModelArk | Here |
|---|---|
| `model: "dreamina-seedance-2-5-260628"` | `model: "seedance-2.5"` |
| `content` item with `text` | `prompt` |
| `image_url` item, role `first_frame` | `start_image: {"url": …}` |
| `image_url` item, role `last_frame` | `end_image: {"url": …}` |
| `image_url` items, role `reference_image` | `reference_images: [{"url": …}]` |
| `video_url` items, role `reference_video` | `reference_videos: [{"url": …}]` |
| `audio_url` items, role `reference_audio` | `reference_audios: [{"url": …}]` |
| `ratio` | `aspect_ratio` (`ratio` is accepted too) |
| `duration: -1` | send 4–30; `-1` only on an edit |
| `omni_reference_task_type: "edit"` | the same |
| `seed` | remove it (rejected) |
| Base64 image data | upload it and pass the `media_url` |
| status `succeeded`, result in `content.video_url` | status `done`, result at `video.url` (`/content`) |

## FAQ

**Do I need a BytePlus or Volcengine account?**
No. One key from this provider is all a request needs; there is no upstream account to configure.

**How long does a job take?**
About 2–5 minutes for a 4–10 second clip, longer when the queue is busy. Poll every 10–15 seconds; there is no webhook.

**How many jobs can run at once?**
Up to 50 Seedance 2.5 jobs per account, whatever the account has spent. A BytePlus individual account runs 3, an enterprise account 10.

**What does a failed job cost?**
Nothing. Rejected requests (`400`), capacity errors (`429`, `503`) and jobs that end `failed` or `expired` are free.

**Can I keep request bodies written for fal or OpenRouter?**
Yes. `image_url`, `end_image_url`, `image_urls`, `video_urls`, `audio_urls`, `frame_images`, `input_references`, `seconds` and `ratio` are accepted as they are; [video-generations.md](./docs/video-generations.md#field-names-from-other-apis) has the full mapping.

**Is the API production-ready?**
Yes. It is stable, jobs that cannot get capacity within 10 minutes fail with a retryable code instead of hanging, and nothing is billed until a video exists.

## Related resources

- [Seedance 2.5 model page](https://argolink.io/en/models/seedance-2.5): live prices, every field, FAQ
- [API guide, Seedance chapter](https://argolink.io/en/docs#/seedance)
- [BytePlus ModelArk pricing](https://docs.byteplus.com/en/docs/modelark/model-pricing) and [Seedance 2.5 guide](https://docs.byteplus.com/en/docs/modelark/seedance-2-5)

## Checking the guides

Every code block in this repository is syntax-checked, every JSON example parsed and every relative link resolved by an offline test:

```bash
pip install pytest
pytest
```

## License

MIT. Seedance is a ByteDance model; this repository is not affiliated with ByteDance or BytePlus.
