# TinyHTTP

Minimal HTTP client.

Default timeout is **30 seconds**. Retries are enabled by default (3 attempts).

```python
from tinyhttp import get, Client

# High-level helper (recommended)
r = get("https://example.com")

# Client
c = Client(timeout=30)
r = c.request("GET", "https://example.com")
```

`Client.request` returns a `Response` with `.json()` always available.
