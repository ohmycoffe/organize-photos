from pathlib import Path

from PIL import Image


def read_image(path: Path) -> Image.Image:
    """Load image as bytes

    Args:
        path (Path): _description_

    Returns:
        Image: _description_
    """
    with Image.open(path) as image:
        image.load()
    return image
