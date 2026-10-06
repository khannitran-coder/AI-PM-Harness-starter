from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ModelRequest:
    system_prompt: str
    user_input: str
    case_id: str


class ModelAdapter(Protocol):
    name: str

    def generate(self, request: ModelRequest) -> dict:
        """Return a JSON-serializable model output matching the task schema."""
        ...
