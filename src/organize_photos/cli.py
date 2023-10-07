from pathlib import Path

import click

from organize_photos.processing import bulk_process_files


@click.command()
@click.argument(
    "source-dir",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        readable=True,
        path_type=Path,
    ),
)
@click.option(
    "-d",
    "--dest-dir",
    required=False,
    default=lambda: Path.cwd() / "output",
    type=click.Path(
        exists=False,
        dir_okay=True,
        file_okay=False,
        writable=True,
        path_type=Path,
    ),
    help="Destination directory where copied and renamed images will be saved.",
)
@click.option(
    "-t",
    "--template",
    required=False,
    default="${year}/${year}${month}${day}${hour}${minute}${second}",
    show_default=True,
    type=click.STRING,
    help="Template for generating new file paths",
)
@click.option(
    "-p",
    "--file-pattern",
    required=False,
    default="**/*",
    show_default=True,
    type=click.STRING,
    help="Pattern for selecting files (UNIX style glob pattern)",
)
def cli(
    source_dir: Path,
    dest_dir: Path,
    template: str,
    file_pattern: str,
) -> None:
    bulk_process_files(
        src_dir=source_dir,
        dst_dir=dest_dir,
        template=template,
        file_pattern=file_pattern,
    )
