import json

from src.smart_crop_service import CropRequest, crop_asset


class FakeResponse:
    status = 200

    def __init__(self, body):
        self.body = body

    def read(self):
        return json.dumps(self.body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_each_requested_ratio_gets_a_crop():
    seen = []

    def opener(request):
        payload = json.loads(request.data.decode())
        seen.append((request.method, request.full_url, payload))
        return FakeResponse({"ok": True, "data": {"url": f"cdn/{payload['aspect']}"}, "error": None, "metadata": {}})

    from src.smart_crop_service import InfraiClient
    result = crop_asset(CropRequest("asset", ("1:1", "16:9")), InfraiClient("test-key", opener))
    assert result == {"1:1": {"url": "cdn/1:1"}, "16:9": {"url": "cdn/16:9"}}
    assert all(item[0] == "POST" and item[1].endswith("/v1/image/smart_crop") for item in seen)
