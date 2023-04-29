from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from organize_photos.cli import cli
from tests.utils import ImageRecipe, create_dirtree


def test_integration_happy_case(
    tmp_path: Path, valid_dirtree_recipe: list[ImageRecipe]
):
    src = tmp_path / "src"
    create_dirtree(recipe=valid_dirtree_recipe, outdir=src)
    expected_number_of_files: int = len(tuple(p for p in src.rglob("*") if p.is_file()))

    runner = CliRunner()
    dst = tmp_path / "dst"

    result = runner.invoke(
        cli=cli,
        args=[
            str(src),
            "--dest-dir",
            str(dst),
            "--template",
            r"${year}/${year}${month}${day}${hour}${minute}${second}-${oldname}",
            "--file-pattern",
            r"**/*",
        ],
    )
    assert result.exit_code == 0
    tested_number_of_files: int = len(tuple(p for p in dst.rglob("*") if p.is_file()))
    assert expected_number_of_files == tested_number_of_files
