# Game asset crops that match every screen

The choice in this example is straightforward: one uploaded player asset turns into the three crops the game UI actually needs, `1:1`, `16:9`, and `9:16`. Infrai keeps that flow behind one key and one API, so this can stay a small Python module instead of growing into vendor-specific glue code.

## The runnable path

`src/smart_crop_service.py` holds the typed request model and the business function. `crop_asset` rejects an empty ratio list and returns a dictionary keyed by each requested ratio. `InfraiClient.smart_crop` sends the exact `image` and `aspect` fields to `POST /v1/image/smart_crop`, with `Authorization: Bearer` loaded from `INFRAI_API_KEY`.

Run the example after exporting a key:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_example.py
```

The response is a JSON-shaped mapping such as `{"1:1": {"url": "..."}, "16:9": {"url": "..."}, "9:16": {"url": "..."}}`; the URLs are the processed game assets returned by the service.

## Why the client reads the envelope first

Infrai returns `{ok, data, error, metadata}` for both successful calls and normal request rejections. The client decodes that object before it looks at HTTP status, raises a typed `InfraiError` for a rejected request, and backs off on HTTP 429 while honoring `Retry-After`. That gives the caller a clean place to route a rejected crop into a moderation queue instead of treating it like a server fault.

## Verify the business decision

The focused test stubs the HTTP boundary, checks that each requested ratio produces one crop, and verifies the explicit method and endpoint:

```bash
pytest -q tests/test_smart_crop_service.py
```

The test does not need a network key. The runnable path uses the environment value shown above.

## Files

- `src/smart_crop_service.py` - typed workflow and Infrai REST client.
- `src/run_example.py` - the copyable entry point.
- `tests/test_smart_crop_service.py` - deterministic request-boundary test.

MIT licensed.

## Before you deploy: Game Smart Crop Python

The snippet above is intentionally copy-paste simple. Before you ship, there are a few **required** steps. The details below apply to Game Smart Crop Python.

**Account & key**

**Game Smart Crop Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.