# Frigobar 
Distribute Python apps to Windows machines without freezing them.

## Basic usage
```
frigobar my_app.py
```
This will create a `frigobar` folder, with a `my_app.bat` file in it. Run it to run your app. And since you already opened it, grab a beer!

## Installation
```
pip install frigobar
```

## Options
```
> frigobar --help
usage: frigobar [-h] [-r REQUIREMENTS_FILE] [-p PYTHON_VERSION] [--copy-directory] script-path [target-directory]

Distribute Python apps to Windows machines without freezing them. The resulting distribution will be put in a folder that   
can be copied to any Windows machine. Users should run "<script_name>.bat" to run the script. All the dependencies,
including an embeddable version of Python, will be downloaded on the first run.

positional arguments:
  script-path           Path to the script to distribute.
  target-directory      Folder where the distribution will be put. Defaults to 'frigobar'.

options:
  -h, --help            show this help message and exit
  -r REQUIREMENTS_FILE, --requirements-file REQUIREMENTS_FILE
                        Path to a requirements file that lists the dependencies of the script.
  -p PYTHON_VERSION, --python-version PYTHON_VERSION, --python PYTHON_VERSION
                        Python version, in X.Y.Z format, that the distribution should use.The version must be available as  
                        an embeddable package on https://www.python.org/downloads/windows/. Defaults to 3.11.4.
  --copy-directory      Copy the contents of the script directory to the distribution.
  --tkinter             Include Tkinter in the distribution.
```

## Rationale
A common technique to distribute Python apps is to "freeze" them using tools like [PyInstaller](https://pyinstaller.org/) or [cx_Freeze](https://cx-freeze.readthedocs.io/). These freezers create a standalone executable that contains your app and all its dependencies. This is a workable solution, but it has two main drawbacks:

1. The resulting frozen app is often huge. It's not uncommon to see a simple app taking MBs of space.
2. Because dependence resolution is hard, the frozen app may contain more or less dependencies than it needs. Less dependencies lead to dread "working-app-that-stop-working-when-you-freeze-it" situations. Unnecessary dependencies lead to bloated apps.

Frigobar avoids those problems by postponing the download of the Python interpreter and all the app's dependencies to the first time the user runs the app, making the app the smallest it can be. Frigobar also doesn't try to be smart about dependencies and will only download the ones explicitly listed in a `requirements.txt` file. This a closer experience to what a developer does when he runs the app in his own machine, which hopefully will lead to less surprises to users.