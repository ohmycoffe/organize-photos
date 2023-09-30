import json
from pathlib import Path

import pytest

TEST_RESOURCES = Path(__file__).parent / "resources"


@pytest.fixture
def valid_dirtree_recipe():
    with open(TEST_RESOURCES / "valid_dirtree_recipe.json") as fp:
        return json.load(fp)
