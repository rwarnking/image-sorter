# Image Sorter

[<img alt="Unit tests" src="https://img.shields.io/github/workflow/status/rwarnking/image-sorter/Run%20Python%20Tests?label=Build&logo=github&style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/actions/workflows/pytests.yml)
[<img alt="Linting status of master" src="https://img.shields.io/github/workflow/status/rwarnking/image-sorter/Lint%20Code%20Base?label=Linter&style=for-the-badge" height="23">](https://github.com/marketplace/actions/super-linter)
[<img alt="Version" src="https://img.shields.io/github/v/release/rwarnking/image-sorter?style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/releases/latest)
[<img alt="Licence" src="https://img.shields.io/github/license/rwarnking/image-sorter?style=for-the-badge" height="23">](https://github.com/rwarnking/image-sorter/blob/main/LICENSE)

## Description
This is a small python application to sort images into folder.
For the sorting proccess either the image name or the image meta data can be used.
All functionalities are accesseable via a simple GUI.

## Table of Contents
- [Image Sorter](#image-sorter)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [GUI](#gui)
  - [Contributing](#contributing)
  - [Credits](#credits)
  - [License](#license)

## List of Features

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
conda env create --file imgsort.txt
```
afterwards activate the environment (`conda activate imgsort`) and start the application.

The main dependency is the anvil tool found here:
* [tkinter](https://docs.python.org/3/library/tkinter.html) for the interface/GUI
* [tkcalendar](https://pypi.org/project/tkcalendar/) for the date selection
* [piexif](https://piexif.readthedocs.io/en/latest/) for modification of the image metadata (EXIF)

Further dependencies that should be present anyway are:
* [datetime](https://docs.python.org/3/library/datetime.html) for all time data objects
* [re (regex)](https://docs.python.org/3/library/re.html) for parsing file names
* [sqlite3](https://docs.python.org/3/library/sqlite3.html) for the database
* [json](https://docs.python.org/3/library/json.html) for event loading and saving
* [threading](https://docs.python.org/3/library/threading.html) used such that the gui is not freezed while processing,
  [Details](https://realpython.com/intro-to-python-threading/)

Optional dependencies for different exif modification methods:
* [pyexiv2](https://github.com/LeoHsiao1/pyexiv2)
* [exif](https://gitlab.com/TNThieding/exif)
* [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/#)

## Usage

Run the program using your usual Python IDE (like Visual Code) or via the console `python src\application.py`

### GUI

The GUI lets you select the input and output directory.
Furthermore options are available to add events and authors.
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
