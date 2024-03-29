# Image Sorter

[<img alt="Unit tests" src="https://img.shields.io/github/actions/workflow/status/rwarnking/image-sorter/pytests.yml?label=Tests&logo=github&style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/actions/workflows/pytests.yml)
[<img alt="Linting status of master" src="https://img.shields.io/github/actions/workflow/status/rwarnking/image-sorter/linter.yml?label=Linter&style=for-the-badge" height="23">](https://github.com/marketplace/actions/super-linter)
[<img alt="Version" src="https://img.shields.io/github/v/release/rwarnking/image-sorter?style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/releases/latest)
[<img alt="Licence" src="https://img.shields.io/github/license/rwarnking/image-sorter?style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/blob/main/LICENSE)

## Description
This is a small python application to sort images into folder.
For the sorting proccess either the image name or the image meta data can be used.
All functionalities are accesseable via a simple GUI.

## Table of Contents
- [Image Sorter](#image-sorter)
  - [Table of Contents](#table-of-contents)
  - [List of Features](#list-of-features)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [GUI](#gui)
  - [Contributing](#contributing)
  - [Credits](#credits)
  - [License](#license)

## List of Features

- Database for events, artists, persons
  - load and save database from json
- Image sorting according to present database data
  - input and output folder selection
  - select input type (filename or metadata)
  - select output signature for folder and file
- Settings for:
  - process folder recursively
  - process unmatched files like (.txt)
  - processing files with identical name
  - require artist for files
  - metadata modifiction
  - metadata overriding
  - save or move files

## Installation

Download this repository or install directly from GitHub
```bash
pip install git+https://github.com/rwarnking/image-sorter.git
```

### Dependencies

This project uses python. One of the tested versions is python 3.9.

Use either
```bash
pip install -r requirements.txt
```
to install all dependencies.

Or use Anaconda for your python environment and create a new environment with
```bash
conda env create --file imgsort.yml
```
afterwards activate the environment (`conda activate imgsort`) and start the application.

The main dependency is tkinter and the piexif tool found here:
* [tkinter](https://docs.python.org/3/library/tkinter.html) for the interface/GUI
* [tkcalendar](https://pypi.org/project/tkcalendar/) for the date selection
* [piexif](https://piexif.readthedocs.io/en/latest/) for modification of the image metadata (EXIF)
* [XlsxWriter](https://pypi.org/project/XlsxWriter/) for writing to excel files
* [openpyxl](https://pypi.org/project/openpyxl/) for reading excel files

Further dependencies that should be present anyway are:
* [datetime](https://docs.python.org/3/library/datetime.html) for all time data objects
* [re (regex)](https://docs.python.org/3/library/re.html) for parsing file names
* [sqlite3](https://docs.python.org/3/library/sqlite3.html) for the database
* [json](https://docs.python.org/3/library/json.html) for event loading and saving
* [threading](https://docs.python.org/3/library/threading.html) used such that the gui is not freezed while processing,
  [Details](https://realpython.com/intro-to-python-threading/)

Alternative exif modification librarys that are no longer used:
* [pyexiv2](https://github.com/LeoHsiao1/pyexiv2)
* [exif](https://gitlab.com/TNThieding/exif)
* [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/#)

## Usage

Run the program using your usual Python IDE (like Visual Code) or via the console `python src\application.py`

### GUI

The GUI lets you select the input and output directory.
Further menus are available to add events and authors to the database.
Progress-bars are given for continuous observation of the progress.

![GUI](/docs/images/gui.jpg)

## Contributing

I encourage you to contribute to this project, in form of bug reports, feature requests
or code additions. Although it is likely that your contribution will not be implemented.

Please check out the [contribution](docs/CONTRIBUTING.md) guide for guidelines about how to proceed
as well as a styleguide.

## Credits
Up until now there are no further contributors other than the repository creator.

## License
This project is licensed under the [MIT License](LICENSE).
