from __future__ import annotations

import datetime
import logging
import shutil
from collections import Counter
from string import Template
from typing import TYPE_CHECKING, Any, Iterable

from PIL import ExifTags

from organize_photos.constants import (
    EXIF_DATETIME_FORMAT,
    SUPPORTED_IMAGE_SUFFIXES,
    VALID_PLACEHOLDERS,
    VALID_PLACEHOLDERS_SET,
)
from organize_photos.loader import read_image
from organize_photos.template_backport import get_identifiers, is_valid

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


_FAILED = "failed"
_SUCCEEDED = "succeeded"
_PROCESSED_FILES = "processed_files"


class _Parts:
    def __init__(
        self,
        expected_parts: set[str],
    ) -> None:
        self._expected_parts = expected_parts
        self._parts: dict

    def _reset(self):
        self._parts = {}

    def __call__(self, path: Path) -> Any:
        self._reset()
        img = read_image(path)
        exif_dict: dict[int, Any] = img._getexif()  # type: ignore[attr-defined] # noqa: SLF001 E501
        if VALID_PLACEHOLDERS.OLDNAME in self._expected_parts:
            self._parts[VALID_PLACEHOLDERS.OLDNAME] = path.stem

        if {
            VALID_PLACEHOLDERS.YEAR,
            VALID_PLACEHOLDERS.MONTH,
            VALID_PLACEHOLDERS.DAY,
            VALID_PLACEHOLDERS.HOUR,
            VALID_PLACEHOLDERS.MINUTE,
            VALID_PLACEHOLDERS.SECOND,
        } & self._expected_parts:
            try:
                self._add_datetime(exif_dict=exif_dict)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    r"Processing 'DateTimeOriginal' field failed {path: '%s': error:"
                    r" '%s'}",
                    path,
                    str(e),
                )
        return self._parts

    def _add_datetime(self, exif_dict: dict):
        date_time_original_str = exif_dict[ExifTags.Base.DateTimeOriginal.value]
        date_time_original_obj = datetime.datetime.strptime(  # noqa: DTZ007
            date_time_original_str,
            EXIF_DATETIME_FORMAT,
        )
        self._parts.update(
            {
                "year": f"{date_time_original_obj.year:02d}",
                "month": f"{date_time_original_obj.month:02d}",
                "day": f"{date_time_original_obj.day:02d}",
                "hour": f"{date_time_original_obj.hour:02d}",
                "minute": f"{date_time_original_obj.minute:02d}",
                "second": f"{date_time_original_obj.second:02d}",
            },
        )


class FilepathCreator:
    def __init__(self, outdir: Path, template: Template) -> None:
        self._outdir = outdir
        self._template = template

    def __call__(self, path: Path) -> Path:
        expected_parts = get_identifiers(self._template)
        parts = _Parts(expected_parts=set(expected_parts))(path=path)
        try:
            name = self._template.substitute(parts)
        except KeyError:
            name = f"default/{path.stem}"
            logger.warning("For '%s' a default path will be created '%s'", path, name)

        return self._outdir / f"{name}{path.suffix}"


def check_template(template: Template):
    if not is_valid(template=template):
        raise RuntimeError(f"Given template '{template.template}' is invalid.")
    unknown_placeholders = set(get_identifiers(template)) - VALID_PLACEHOLDERS_SET
    if unknown_placeholders:
        raise RuntimeError(
            f"Unknown placeholders given {unknown_placeholders} in"
            f" '{template.template}'.",
        )


def process(
    src_dir: Path,
    dst_dir: Path,
    template: str,
    file_pattern: str = "**/*",
    is_dry_run: bool = False,  # noqa: FBT002 FBT001
) -> None:
    """
    Copy files from source_directory to destination_directory based on a path template.

    Args:
        src_dir (Path): Source directory.
        dst_dir (Path): Destination directory.
        template (str): Template for generating new file paths.
        file_pattern (str): Pattern for selecting files (UNIX style glob pattern).
        is_dry_run (bool): If True, perform a dry run without actually copying files.

    Returns:
        None
    """
    files = (p for p in src_dir.glob(pattern=file_pattern) if p.is_file())
    t = Template(template=template)
    check_template(t)
    fc = FilepathCreator(outdir=dst_dir, template=t)

    process_files(
        src_filepaths=files,
        filepath_creator=fc,
        is_dry_run=is_dry_run,
    )


def process_files(
    src_filepaths: Iterable[Path],
    filepath_creator: FilepathCreator,
    is_dry_run: bool = False,  # noqa: FBT001 FBT002
) -> None:
    stats = Counter(**{_PROCESSED_FILES: 0, _SUCCEEDED: 0, _FAILED: 0})
    for it, oldfilepath in enumerate(src_filepaths):
        logger.debug("(%d) Processing %s...", it, oldfilepath)
        if not oldfilepath.is_file():
            logger.warning("'%s' is not a file - skipping.", oldfilepath)
            continue
        stats[_PROCESSED_FILES] += 1
        try:
            suffix = oldfilepath.suffix
            stats[suffix] += 1
            if suffix not in SUPPORTED_IMAGE_SUFFIXES:
                raise RuntimeError(  # noqa: TRY301
                    f"Suffix '{suffix}' is not supportrd",
                )
            newfilepath = filepath_creator(path=oldfilepath)
            if not is_dry_run:
                newfilepath.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src=str(oldfilepath), dst=str(newfilepath))
            logger.info("Copy file from '%s' to '%s'.", oldfilepath, newfilepath)
            stats[_SUCCEEDED] += 1
        except Exception:
            logger.exception("Failed to process %s. Will be skipped.", oldfilepath)
            stats[_FAILED] += 1

    logger.info(
        "Processing finished. Processed %s files. Succeeded %s. Failed %s",
        stats[_PROCESSED_FILES],
        stats[_SUCCEEDED],
        stats[_FAILED],
    )
    logger.debug("%s", dict(stats))
