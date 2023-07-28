# Refrigerator 
Distribute Python apps to Windows machines without freezing them.

## Basic usage
```
refrigerator my_app.py
```
This will create a `refrigerator` folder, with a `my_app.bat` file in it. Run it to run your app. And since you already opened it, grab a beer!

## Installation
```
pip install refrigerator
```

## Options
```
refrigerator --help
```

## Rationale
A common technique to distribute Python apps is to "freeze" them using tools like [PyInstaller](https://pyinstaller.org/) or [cx_Freeze](https://cx-freeze.readthedocs.io/). These freezers create a standalone executable that contains your app and all its dependencies. This is a workable solution, but it has two main drawbacks:

1. The resulting frozen app is often huge. It's not uncommon to see a simple app taking MBs of space.
2. Because dependence resolution is hard, the frozen app may contain more or less dependencies than it needs. Less dependencies lead to dread "working-app-that-stop-working-when-you-freeze-it" situations. Unnecessary dependencies lead to bloated apps.

Refrigerator avoids those problems by postponing the download of the Python interpreter and all the app's dependencies to the first time the user runs the app, making the app the smallest it can be. Refrigerator also doesn't try to be smart about dependencies and will only download the ones explicitly listed in a `requirements.txt` file. This a closer experience to what a developer does when he runs the app in his own machine, which hopefully will lead to less surprises to users.