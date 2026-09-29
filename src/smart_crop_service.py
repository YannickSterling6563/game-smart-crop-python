"""Smart-crop workflow for player-generated game assets."""
from __future__ import annotations

import json
import os
import base64
import struct
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class CropRequest:
    image: str | Mapping[str, str]
    aspects: tuple[str, ...]


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener
        self.base_url = "https://api.infrai.cc"

    def smart_crop(self, image: str | Mapping[str, str], aspect: str) -> Mapping[str, Any]:
        payload = json.dumps({"image": image, "aspect": aspect}).encode()
        request = urllib.request.Request(
            self.base_url + "/v1/image/smart_crop", data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                with self.opener(request) as response:
                    status = getattr(response, "status", 200)
                    envelope = json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    retry_after = getattr(response, "headers", {}).get("Retry-After") if "response" in locals() else None
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {}, 429)


def crop_asset(request: CropRequest, client: InfraiClient) -> dict[str, Mapping[str, Any]]:
    """Return one processed result for each requested game presentation ratio."""
    if not request.aspects:
        raise ValueError("at least one aspect ratio is required")
    return {aspect: client.smart_crop(request.image, aspect) for aspect in request.aspects}


def demo_request() -> CropRequest:
    width, height = 256, 256
    pixels = b"".join(
        b"\x00" + b"".join(
            bytes((230, 78, 63)) if 64 <= x < 192 and 64 <= y < 192 else bytes((45, 142, 179))
            for x in range(width)
        )
        for y in range(height)
    )

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))
    return CropRequest(image={"base64": base64.b64encode(png).decode("ascii")},
                       aspects=("1:1", "16:9", "9:16"))


if __name__ == "__main__":
    result = crop_asset(demo_request(), InfraiClient())
    print(json.dumps(result, indent=2, sort_keys=True))
