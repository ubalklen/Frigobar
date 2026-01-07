# Frigobar 
Distribute Python scripts to Windows machines without freezing them.

## Basic usage
```
frigobar my_script.py
```
This will create a `frigobar` folder, with a `my_script.bat` file in it. Run it to run your app.

## Advanced usage
Frigobar supports two modes of dependency management:

### Modern dependencies (Recommended)
In this mode, you declare your dependencies either in a `pyproject.toml` file in the same directory as your script, or using [inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) (PEP 723) directly in your script file.

Frigobar will automatically detect `pyproject.toml` or inline metadata and configure the distribution to use `uv` for dependency resolution and Python version management.

**Example with inline metadata:**
```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "pandas",
# ]
# ///
import requests
import pandas
```

**Usage:**
```bash
frigobar my_script.py
```

**Using a custom pyproject.toml path:**
```bash
frigobar my_script.py -t /path/to/custom/pyproject.toml
```

### Classical dependencies
In this mode, you provide a standard `requirements.txt` file. You can also optionally specify the Python version to be used.

**Usage:**
```bash
frigobar my_script.py -r requirements.txt
```

Or specifying a Python version:
```bash
frigobar my_script.py -r requirements.txt -p 3.12.0
```

### Environment Variables
You can set environment variables that will be available when the script runs:

```bash
frigobar my_script.py --env-var MY_VAR=value --env-var ANOTHER_VAR=123
```

These environment variables will be set in the generated batch file and will be available to your Python script when it runs.

## Installation
```
pip install frigobar
```

## Options
```
> frigobar --help
usage: cli.py [-h] [-t PYPROJECT_FILE] [-r REQUIREMENTS_FILE] [-p PYTHON_VERSION] [--copy-directory] [-e ENV_VAR] script-path [target-directory]

Distribute Python scripts to Windows machines without freezing them. The folder of the resulting distribution can be copied to any Windows machine. Users should run "<script_name>.bat" to run the script. All the dependencies, including Python, will be downloaded and installed on the first run.

positional arguments:
  script-path           Path to the script to distribute.
  target-directory      Folder where the distribution will be put. Defaults to 'frigobar'.

options:
  -h, --help            show this help message and exit
  -t PYPROJECT_FILE, --pyproject-file PYPROJECT_FILE
                        Path to a pyproject.toml file that contains the dependencies of the script. If not provided, the tool will look for a pyproject.toml file in the script's directory. Cannot be used together with --requirements-file.
  -r REQUIREMENTS_FILE, --requirements-file REQUIREMENTS_FILE
                        Path to a classical requirements file (usually called requirements.txt) that lists the dependencies of the script. If not provided, dependencies must be declared in a pyproject.toml file or inline.
  -p PYTHON_VERSION, --python-version PYTHON_VERSION, --python PYTHON_VERSION
                        Python version, in X.Y.Z format, that the distribution should use. Only works when --requirements-file is specified. If not provided, the latest Python supported by the final user's system will be used.
  --copy-directory      Copy the contents of the script directory to the distribution. Respects .gitignore if present.
  -e ENV_VAR, --env-var ENV_VAR
                        Set environment variables in the generated batch file. Format: KEY=VALUE. Can be used multiple times to set multiple variables. Example: --env-var MY_VAR=value --env-var ANOTHER_VAR=123
```

## Rationale
A common technique to distribute Python apps is to "freeze" them using tools like [PyInstaller](https://pyinstaller.org/) or [cx_Freeze](https://cx-freeze.readthedocs.io/). These freezers create a standalone executable that contains your app and all its dependencies. This is a workable solution, but it has two main drawbacks:

1. The resulting frozen app is often huge. It's not uncommon to see a simple app taking MBs of space.
2. Because dependence resolution is hard, the frozen app may contain more or less dependencies than it needs. Less dependencies lead to dread "working-app-that-stop-working-when-you-freeze-it" situations. Unnecessary dependencies lead to bloated apps.

Frigobar avoids those problems by postponing the download of the Python interpreter and all the app's dependencies to the first time the user runs the app, making the app the smallest it can be. Under the hood, Frigobar uses [uv](https://github.com/astral-sh/uv), an extremely fast Python package installer and resolver. This ensures a robust and reproducible environment setup, supporting both modern (pyproject.toml, inline metadata) and classical (requirements.txt) dependency definitions.