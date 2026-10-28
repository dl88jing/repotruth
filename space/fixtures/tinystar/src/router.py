"""TinyStar router — drifts vs README."""
from __future__ import annotations
from typing import Any, Callable


class Router:
    def __init__(self) -> None:
        self._routes: list[tuple[str, tuple[str, ...], Callable]] = []
        self._middleware: list[Callable] = []

    def route(self, path: str, methods: list[str] | None = None):
        """Register a route. Handler may be sync or async — we do NOT require async."""
        methods_t = tuple(m.upper() for m in (methods or ["GET"]))

        def deco(fn: Callable):
            # Path params use {id} not :id (drift vs README)
            self._routes.append((path, methods_t, fn))
            return fn

        return deco

    def use(self, mw: Callable) -> None:
        """Middleware runs BEFORE the handler (drift vs README 'after')."""
        self._middleware.append(mw)

    def match(self, method: str, path: str) -> Callable | None:
        for p, methods, fn in self._routes:
            if path == p and method.upper() in methods:
                return fn
        return None
