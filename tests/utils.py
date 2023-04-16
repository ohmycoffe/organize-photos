from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
import piexif
from PIL import Image

from organize_photos.constants import EXIF_DATETIME_FORMAT, SUPPORTED_IMAGE_SUFFIXES

_ALPHABET = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


class RandomValuesGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = np.random.default_rng(seed)

    def get_datetime(self, min_year: int, max_year: int) -> datetime.datetime:
        year: int = self.rng.integers(low=min_year, high=max_year, endpoint=True)
        month: int = self.rng.integers(low=1, high=12, endpoint=True)
        day: int = self.rng.integers(low=1, high=28, endpoint=True)
        hour: int = self.rng.integers(low=0, high=24)
        minute: int = self.rng.integers(low=0, high=60)
        second: int = self.rng.integers(low=0, high=60)
        return datetime.datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
        )

    def get_image(self, min_size: int, max_size: int) -> Image.Image:
        size = (
            *self.rng.integers(
                low=min_size,
                high=max_size,
                size=2,
                endpoint=True,
            ),
            3,
        )
        array = self.rng.integers(low=0, high=256, size=size, dtype=np.uint8)
        return Image.fromarray(array)

    def get_string(self, min_length: int, max_length: int) -> str:
        return "".join(
            self.rng.choice(
                a=_ALPHABET,
                size=self.rng.integers(min_length, max_length, endpoint=True),
            ),
        )

    def get_dirpath(
        self,
        min_length: int,
        max_length: int,
        max_depth: int,
    ) -> Path:
        p = Path(
            *[
                self.get_string(min_length, max_length)
                for _ in range(self.rng.integers(max_depth, endpoint=True))
            ],
        )

        return p

    def get_filename(
        self,
        min_length: int,
        max_length: int,
        suffixes: list[str],
    ) -> str:
        stem = self.get_string(min_length=min_length, max_length=max_length)
        suffix = self.rng.choice(suffixes)
        return f"{stem}{suffix}"


class ImageRecipe(TypedDict):
    path: str
    exif: dict[str, Any] | None


def create_random_recipe(
    num: int,
    rng: RandomValuesGenerator,
) -> list[ImageRecipe]:
    """Create a recipe for images generation

    Args:
        num (int): Number of images to generate
        rfg (RandomFieldsGenerator): Random fields generator instance
    """
    dirs = [
        str(rng.get_dirpath(min_length=3, max_length=5, max_depth=2))
        for _ in range(num)
    ]
    res: list[ImageRecipe] = []
    for _ in range(num):
        timestamp = rng.get_datetime(
            min_year=2000,
            max_year=2030,
        )
        artist = rng.rng.choice(a=["PersonA", "PersonB", "PersonC"])
        dirpath = rng.rng.choice(dirs)
        filename = rng.get_filename(
            min_length=3,
            max_length=7,
            suffixes=SUPPORTED_IMAGE_SUFFIXES,
        )
        res.append(
            ImageRecipe(
                path=str(Path(dirpath, filename)),
                exif={
                    "0th": {piexif.ImageIFD.Artist: artist},
                    "Exif": {
                        piexif.ExifIFD.DateTimeOriginal: timestamp.strftime(
                            EXIF_DATETIME_FORMAT,
                        ),
                    },
                },
            ),
        )
    return res


def create_dirtree(
    recipe: list[ImageRecipe],
    outdir: Path,
) -> None:
    rng = RandomValuesGenerator(1)
    for data in recipe:
        image = rng.get_image(min_size=150, max_size=300)
        path = outdir / data["path"]
        path.parent.mkdir(exist_ok=True, parents=True)
        exif_dict = data["exif"]
        if exif_dict is not None:
            exif = piexif.dump(exif_dict)
            image.save(path, exif=exif)
        else:
            image.save(path)


def create_random_dirtree(num: int, out: Path, seed: int | None = None) -> None:
    rng = RandomValuesGenerator(seed)
    shutil.rmtree(out, ignore_errors=True)
    recipe_path = out / "valid_images_tree.json"
    recipe = create_random_recipe(num=num, rng=rng)
    with open(recipe_path, "w") as fp:
        json.dump(obj=recipe, fp=fp)

    with open(recipe_path) as fp:
        data = json.load(fp=fp)
        create_dirtree(recipe=data, outdir=out / "src")
