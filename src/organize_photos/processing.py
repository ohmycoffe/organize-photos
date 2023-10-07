from __future__ import annotations

import datetime
import logging
import shutil
from string import Template
from typing import TYPE_CHECKING, Any, Callable, Iterable

from PIL import ExifTags

from organize_photos.constants import (
    EXIF_DATETIME_FORMAT,
    SUPPORTED_IMAGE_SUFFIXES,
    VALID_PLACEHOLDERS,
    VALID_PLACEHOLDERS_SET,
)
from organize_photos.fileinfo import FileInfo, Status
from organize_photos.loader import read_image
from organize_photos.template_backport import get_identifiers, is_valid

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class ExtractExif:
    def __init__(
        self,
        expected_parts: set[str],
    ) -> None:
        self._expected_parts = expected_parts
        self._parts: dict[str, int | str]

    def _reset(self) -> None:
        self._parts = {}

    def __call__(self, path: Path) -> Any:
        self._reset()
        img = read_image(path)
        exif_dict: dict[int, Any] = img._getexif()  # type: ignore # noqa: SLF001
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
                self._add_datetime(exif_dict=exif_dict)  # pyright: ignore
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    r"Processing 'DateTimeOriginal' field failed {path: '%s': error:"
                    r" '%s'}",
                    path,
                    str(e),
                )
        return self._parts

    def _add_datetime(self, exif_dict: dict[int, Any]) -> None:
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


class NameCreator:
    def __init__(self, template: Template) -> None:
        self._template = template
        self._extract_exif_data = ExtractExif(
            expected_parts=set(
                get_identifiers(template=template),
            ),
        )

    def __call__(self, path: Path) -> str:
        parts = self._extract_exif_data(path=path)
        try:
            name = self._template.substitute(parts)
        except KeyError:
            name = f"default/{path.stem}"
            logger.warning("For '%s' a default path will be created '%s'", path, name)
        except Exception:
            logger.exception("Unexpected error occurred.")
            raise
        return name


def check_template(template: Template) -> None:
    if not is_valid(template=template):
        raise RuntimeError(f"Given template '{template.template}' is invalid.")
    unknown_placeholders = set(get_identifiers(template)) - VALID_PLACEHOLDERS_SET
    if unknown_placeholders:
        raise RuntimeError(
            f"Unknown placeholders given {unknown_placeholders} in"
            f" '{template.template}'.",
        )


def get_fileinfo(
    path: Path,
    name_create_call: Callable[[Path], str],
    supported_suffixes: list[str] = SUPPORTED_IMAGE_SUFFIXES,
) -> FileInfo:
    f = FileInfo(src=path)
    try:
        suffix = f.src.suffix
        if f.src.suffix not in supported_suffixes:
            f.errors.append(
                RuntimeError(
                    f"Suffix '{suffix}' is not supported",
                ),
            )
            f.status = Status.FAILED
            return f
        f.dst = name_create_call(path)
        f.status = Status.SUCCEEDED
    except Exception as e:  # noqa: BLE001
        f.errors.append(e)
        f.status = Status.FAILED
    return f


def copy(file_info: FileInfo, dst_dir: Path) -> None:
    path = dst_dir / f"{file_info.dst}{file_info.src.suffix}"
    if path.exists():
        count = 1
        while path.exists():
            logger.warning("Path `%s` already exists.", path)
            count += 1
            path = dst_dir / f"{file_info.dst}_{count}{file_info.src.suffix}"
    logger.info("Copy file `%s` to `%s`.", file_info.src, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src=str(file_info.src), dst=str(path))


def process_files(
    files: Iterable[Path],
    dst_dir: Path,
    create_name_call: Callable[[Path], str],
) -> None:
    """
    Copy all `files` to `dst_dir`.
    Newly created files would be renamed according to given rules defined in
    `name_creator` instance.

    Args:
        files (Path): Source files.
        dst_dir (Path): Destination directory.
        create_name_call (Callable):  callable that rename filename
    Returns:
        None
    """
    for p in files:
        if not p.is_file():
            continue
        logger.debug("Process `%s", p)
        file_info = get_fileinfo(
            path=p,
            name_create_call=create_name_call,
            supported_suffixes=SUPPORTED_IMAGE_SUFFIXES,
        )
        if file_info.status is not Status.SUCCEEDED:
            for err in file_info.errors:
                logger.error("Failed `%s`: `%s`", file_info.src, err)
            continue
        copy(file_info=file_info, dst_dir=dst_dir)


def bulk_process_files_in_srcdir(
    src_dir: Path,
    dst_dir: Path,
    template: str,
    file_pattern: str,
) -> None:
    """
    Copy all files which match `file_pattern` from `src_dir` to `dst_dir`.
    Newly created files would be renamed according to given `template`.

    Args:
        src_dir (Path): Source directory.
        dst_dir (Path): Destination directory.
        template (str): Template for generating new file paths.
        file_pattern (str): Pattern for selecting files (UNIX style glob pattern).

    Returns:
        None
    """
    t = Template(template)
    check_template(t)
    nc = NameCreator(template=t)
    process_files(
        files=src_dir.glob(file_pattern),
        dst_dir=dst_dir,
        create_name_call=nc,
    )
