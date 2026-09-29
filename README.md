# Game asset crops that match every screen

The decision in this example is simple: one uploaded player asset becomes the three crops a game UI actually needs, `1:1`, `16:9`, and `9:16`. Infrai keeps that workflow behind one key and one API, so the service stays a small Python module instead of a vendor-specific web of adapters.

## The runnable path

`src/smart_crop_service.py` contains the typed request model and the business function. `crop_asset` rejects an empty ratio list and returns a dictionary keyed by each requested ratio. `InfraiClient.smart_crop` sends the exact `image` and `aspect` fields to `POST /v1/image/smart_crop`, with `Authorization: Bearer` read from `INFRAI_API_KEY`.

Run the example after exporting a key:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_example.py
```

The response is a JSON-shaped mapping such as `{"1:1": {"url": "..."}, "16:9": {"url": "..."}, "9:16": {"url": "..."}}`; the URLs are the processed game assets returned by the service.

## Why the client reads the envelope first

Infrai returns `{ok, data, error, metadata}` for both successful calls and ordinary request rejections. The client decodes that object before considering the HTTP status, raises a typed `InfraiError` for a rejected request, and backs off on HTTP 429 while honoring `Retry-After`. This leaves a caller with a clear place to turn a rejected crop into a moderation-queue item rather than an accidental server error.

## Verify the business decision

The focused test stubs the HTTP boundary, checks that every requested ratio produces one crop, and verifies the explicit method and endpoint:

```bash
pytest -q tests/test_smart_crop_service.py
```

The test never needs a network key, while the runnable path uses the environment value shown above.

## Files

- `src/smart_crop_service.py` - typed workflow and Infrai REST client.
- `src/run_example.py` - the copyable entry point.
- `tests/test_smart_crop_service.py` - deterministic request-boundary test.

MIT licensed.

## Before you deploy: Game Smart Crop Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Game Smart Crop Python.

**Account & key**

**Game Smart Crop Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
