import datetime
import json
import logging
import shutil
from collections import Counter
from pathlib import Path

from exif import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROP_DATETIME = "datetime"
DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"
TIME_SEP = "T"


def _get_img_timestamp(img: Image) -> datetime.datetime:
    timestamp_str = img.get(PROP_DATETIME)
    if not timestamp_str:
        raise ValueError(
            f"Expected datetime as 'YYYY:MM:DD hh:mm:ss' - got {timestamp_str} instead"
        )
    timestamp = datetime.datetime.strptime(timestamp_str, DATETIME_FORMAT)
    return timestamp


def _get_timestamp_as_str(timestamp: datetime.datetime):
    return (
        timestamp.isoformat(timespec="seconds", sep=TIME_SEP)
        .replace("-", "")
        .replace(":", "")
    )


class FilepathCreator:
    def __init__(self, rootdir: Path) -> None:
        self._repetitions: Counter = Counter()
        self._rootdir = rootdir

    def __call__(self, old: Path) -> Path:
        with open(old, "rb") as img_file:
            img = Image(img_file)
        try:
            timestamp = _get_img_timestamp(img)
            prefix = _get_timestamp_as_str(timestamp)
            subdir = str(timestamp.year)
        except ValueError:
            prefix = old.stem
            subdir = "Unknown"

        self._repetitions[prefix] += 1
        if self._repetitions[prefix] > 1:
            prefix = f"{prefix}_{self._repetitions[prefix]}"

        newfilename = f"{prefix}{old.suffix}"
        return self._rootdir / subdir / newfilename


def process(dirpath: Path, out: Path):
    files = tuple(p for p in dirpath.rglob("*") if p.is_file())
    fc = FilepathCreator(out)
    errors = {}
    for oldfilepath in files:
        logger.debug("File: %s", oldfilepath)
        try:
            newfilepath = fc(oldfilepath)
            if newfilepath.exists():
                raise FileExistsError("File %s exists.", newfilepath)
        except Exception as e:
            logging.error(
                "Error occurred while processing file %s. It will be skipped.",
                oldfilepath,
            )
            errors[str(oldfilepath)] = str(e)
            continue
        newfilepath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(oldfilepath), str(newfilepath))
        logger.info("File: %s copied to %s", oldfilepath, newfilepath)

    # postprocessing
    # I want to be 100% sure if I do not overwrite something - so i gather info how
    # many files were generated
    num_of_copied_files = len(tuple(p for p in out.rglob("*") if p.is_file()))
    num_of_errors = len(errors)
    num_of_files = len(files)
    msg = (
        "Summary: %s files in directory '%s' has been copied to %s files in directory"
        " '%s'. %s errors has occurred."
        % (num_of_files, dirpath, num_of_copied_files, out, num_of_errors)
    )
    logger.info(msg)
    if errors:
        for err_file, err_msg in errors.items():
            logger.warning("Skipped file %s caused by exception: %s", err_file, err_msg)
        dump_file = (
            out / f"{_get_timestamp_as_str(datetime.datetime.now())}_errors.json"
        )
        logger.info("Saving debug info to: %s", str(dump_file))
        with open(dump_file, "w") as outfile:
            json.dump(errors, outfile, indent=1, ensure_ascii=False)


process(
    dirpath=Path("/mnt/c/Users/kkrolikowski/Desktop/raw_ph/"),
    out=Path("/mnt/c/Users/kkrolikowski/Desktop/photos"),
)
