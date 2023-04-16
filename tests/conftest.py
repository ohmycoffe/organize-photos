from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

TEST_RESOURCES = Path(__file__).parent / "resources"


@pytest.fixture
def valid_dirtree_recipe() -> Any:
    def strtointkey(d: dict[Any, Any]) -> dict[Any, Any]:
        nd = {}
        for k, v in d.items():
            try:
                k = int(k)  # noqa: PLW2901
            except ValueError:
                pass
            nd[k] = v
        return nd

    with open(TEST_RESOURCES / "valid_dirtree_recipe.json") as fp:
        data = json.load(fp, object_hook=strtointkey)

    return data
