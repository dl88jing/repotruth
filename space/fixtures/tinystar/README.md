# TinyStar

Tiny ASGI-ish router for demos.

## Quick start

```python
from tinystar import Router

app = Router()

@app.route("/health", methods=["GET"])
async def health(request):
    return {"ok": True}
```

`Router.route` is an **async** decorator. Middleware registered with `app.use()` runs **after** the handler (post-processing only).
Path params use `:id` syntax (`/users/:id`).
