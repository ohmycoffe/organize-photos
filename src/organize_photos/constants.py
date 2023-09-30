from __future__ import annotations

import dataclasses

EXIF_DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"


@dataclasses.dataclass(frozen=True)
class _ValidPlaceholders:
    YEAR: str = "year"
    DAY: str = "day"
    MONTH: str = "month"
    HOUR: str = "hour"
    MINUTE: str = "minute"
    SECOND: str = "second"
    OLDNAME: str = "oldname"


VALID_PLACEHOLDERS = _ValidPlaceholders()
VALID_PLACEHOLDERS_SET: set[str] = set(dataclasses.asdict(VALID_PLACEHOLDERS).values())
SUPPORTED_IMAGE_SUFFIXES = [".jpeg", ".jpg"]
