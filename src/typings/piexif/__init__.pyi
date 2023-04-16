from typing import Any

from ._exif import *  # noqa: F403

def dump(exif_dict_original: dict[Any, Any]) -> Any | bytes: ...
