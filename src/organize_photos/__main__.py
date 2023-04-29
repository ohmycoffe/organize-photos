import logging

from organize_photos.cli import cli

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    cli()
