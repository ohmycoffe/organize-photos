# organize-photos

[![PyPI - Version](https://img.shields.io/pypi/v/organize-photos)](https://pypi.org/project/organize-photos/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/organize-photos)
[![Test and lint](https://github.com/ohmycoffe/organize-photos/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ohmycoffe/organize-photos/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/ohmycoffe/organize-photos/graph/badge.svg?token=PAN0F7B4E8)](https://codecov.io/gh/ohmycoffe/organize-photos)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
![PyPI - License](https://img.shields.io/pypi/l/organize-photos)

The `organize-photos` is a Python CLI program that allows you to organize your photos into subfolders based on their EXIF metadata. You can define a custom pattern to create new paths for your photos, making it easy to sort and categorize your image collection.

## Features

- Organize photos based on EXIF metadata such as date and time taken.
- Customize the path structure using a template with placeholders for year, month, day, hour, minute, and second.
- Copy and rename images to the destination directory, maintaining the folder structure specified by the template.
- Supports UNIX-style glob patterns for selecting files in the source directory.

## Installation

### Development
Prerequisites: [pdm](https://pdm.fming.dev/latest/) for environment management 
1. Clone this repository.

```bash
git clone https://github.com/ohmycoffe/organize-photos.git
```

2. Navigate to the project directory.

```bash
cd organize-photos
```

3. Install the required dependencies using pdm.

```bash
pdm install -G dev
```
Install pre-commit.
```bash
pdm run pre-commit install
```

4. Run tests.

```bash
pdm run pytest
```
> **_NOTE:_**  This repository supports also GNU Make commands
```bash
make help
```

## Usage

You can easily install the latest released version using binary installers from the Python Package Index (PyPI):

```sh
pip install organize-photos --user
```

- `source-dir`: The source directory containing the photos you want to organize.
- `-d, --dest-dir`: The destination directory where copied and renamed images will be saved. If not provided, the default is the current working directory.
- `-t, --template`: The template for generating new file paths. Customize the path structure using placeholders such as `${year}`, `${month}`, `${day}`, `${hour}`, `${minute}`, and `${second}`.
- `-p, --file-pattern`: The pattern for selecting files in the source directory. Use UNIX-style glob patterns to filter which files will be processed. The default is to process all files.

## Example

```bash
organize-photos /path/to/source/photos -d /path/to/output -t "${year}/${year}${month}${day}${hour}${minute}${second}"
```

This command will organize the photos in the source directory based on the specified template and file pattern and save the organized photos in the destination directory.
For instance, if you have a file located at `/path/to/source/photos/image1.jpg`, which was created on `January 3, 2019, at 20:54:12`, the program creates a copy of the file at `/path/to/output/2019/20190103205412.jpg` following the specified pattern.

## License

`organize-photos` is released under the [MIT License](LICENSE).

## Author

- ohmycoffe
- GitHub: [ohmycoffe](https://github.com/ohmycoffe)
