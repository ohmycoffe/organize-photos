
# organize-photos

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
organize-photos /path/to/source/photos -d /path/to/output -t "${year}/${year}${month}${day}${hour}${minute}${second}" -p "**/*.jpg"
```

This command will organize the photos in the source directory based on the specified template and file pattern and save the organized photos in the destination directory.
For instance, if you have a file located at `/path/to/source/photos/image1.jpeg`, which was created on `January 3, 2019, at 20:54:12`, the program creates a copy of the file at `/path/to/output/2019/20190103205412.jpeg` following the specified pattern.

## License

`organize-photos` is released under the [MIT License](LICENSE).

## Author

- ohmycoffe
- GitHub: [ohmycoffe](https://github.com/ohmycoffe)
