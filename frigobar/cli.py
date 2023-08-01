import argparse

from frigobar import frigobar


def create_frigobar(args):
    frigobar.create_frigobar(
        script_path=args.script_path,
        target_directory=args.target_directory,
        requirements_file=args.requirements_file,
        python_version=args.python_version,
        copy_directory=args.copy_directory,
        tkinter=args.tkinter,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Distribute Python apps to Windows machines without freezing them. The "
            "resulting distribution will be put in a folder that can be copied to any "
            'Windows machine. Users should run "<script_name>.bat" to run the script. '
            "All the dependencies, including an embeddable version of Python, will be "
            "downloaded on the first run."
        )
    )
    parser.add_argument(
        "script_path", metavar="script-path", help="Path to the script to distribute."
    )
    parser.add_argument(
        "target_directory",
        metavar="target-directory",
        default="frigobar",
        nargs="?",
        help="Folder where the distribution will be put. Defaults to 'frigobar'.",
    )
    parser.add_argument(
        "-r",
        "--requirements-file",
        help="Path to a requirements file that lists the dependencies of the script.",
    )
    parser.add_argument(
        "-p",
        "--python-version",
        "--python",
        default="3.11.4",
        help=(
            "Python version, in X.Y.Z format, that the distribution should use."
            "The version must be available as an embeddable package on "
            "https://www.python.org/downloads/windows/. Defaults to 3.11.4."
        ),
    )
    parser.add_argument(
        "--copy-directory",
        action="store_true",
        help="Copy the contents of the script directory to the distribution.",
    )
    parser.add_argument(
        "--tkinter",
        action="store_true",
        help="Include Tkinter in the distribution.",
    )
    args = parser.parse_args()
    create_frigobar(args)


if __name__ == "__main__":
    main()
