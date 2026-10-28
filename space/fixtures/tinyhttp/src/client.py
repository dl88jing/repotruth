"""TinyHTTP client — drifts vs README."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


DEFAULT_TIMEOUT = 5.0  # README says 30 (drift #1)
DEFAULT_RETRIES = 0    # README says 3 (drift #2)


@dataclass
class Response:
    status_code: int
    text: str
    headers: dict[str, str]

    def json(self) -> Any:
        # Only works when content-type is json; otherwise raises (drift #3)
        import json
        if "application/json" not in self.headers.get("content-type", ""):
            raise ValueError("not JSON")
        return json.loads(self.text)


class Client:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT, retries: int = DEFAULT_RETRIES):
        self.timeout = timeout
        self.retries = retries

    def request(self, method: str, url: str) -> Response:
        # stub — no network in fixtures
        return Response(200, "{}", {"content-type": "application/json"})


def get(url: str) -> Response:
    return Client().request("GET", url)
