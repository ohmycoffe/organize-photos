from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Status(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class FileInfo:
    src: Path
    status: Status | None
    dst: str | None
    errors: list[Exception]

    def __init__(self, src: Path) -> None:
        self.src = src
        self.status = None
        self.dst = None
        self.errors = []
