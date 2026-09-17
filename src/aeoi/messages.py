"""User-facing check messages in several languages.

A :class:`Msg` is a ``str`` (its English rendering, so every existing caller and test keeps
working) that also remembers its catalogue id and parameters, so it can be rendered in another
language later: ``msg.text("de")``. Templates live in ``messages.json`` (``{id: {lang: text}}``,
``str.format`` placeholders). A parameter may itself be a :class:`Msg`; it is rendered in the
requested language too (e.g. the reason inside a character-set finding).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

CATALOGUE = Path(__file__).with_name("messages.json")
LANGUAGES = ("en", "de")


@lru_cache(maxsize=1)
def catalogue() -> dict[str, dict[str, str]]:
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def render(msg_id: str, lang: str, params: dict[str, Any]) -> str:
    entry = catalogue()[msg_id]
    template = entry.get(lang) or entry["en"]
    values = {k: _value(v, lang) for k, v in params.items()}
    return template.format_map(values)


def _value(v: Any, lang: str) -> Any:
    if isinstance(v, Msg):
        return v.text(lang)
    if isinstance(v, (list, tuple)) and v and all(isinstance(x, str) for x in v):
        if any(isinstance(x, Msg) for x in v):  # several findings: one sentence each
            return "; ".join(x.text(lang) if isinstance(x, Msg) else x for x in v)
        return ", ".join(v)  # plain values such as country codes
    return v


class Msg(str):
    """A message that is an English string now and any catalogue language on request."""

    __slots__ = ("id", "params")

    def __new__(cls, msg_id: str, **params: Any) -> Self:
        obj = super().__new__(cls, render(msg_id, "en", params))
        obj.id = msg_id
        obj.params = params
        return obj

    def text(self, lang: str = "en") -> str:
        return render(self.id, lang, self.params)

    def __reduce__(self):  # pickling (multiprocessing, caches): rebuild from id + params
        return (Msg._rebuild, (self.id, self.params))

    @staticmethod
    def _rebuild(msg_id: str, params: dict[str, Any]) -> Msg:
        return Msg(msg_id, **params)


def text(message: str, lang: str = "en") -> str:
    """Render a message that may or may not be a :class:`Msg`."""
    return message.text(lang) if isinstance(message, Msg) else message
