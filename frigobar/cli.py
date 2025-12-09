import argparse

from frigobar import frigobar


def create_frigobar(args):
    frigobar.create_frigobar(
        script_path=args.script_path,
        target_directory=args.target_directory,
        requirements_file=args.requirements_file,
        python_version=args.python_version,
        timestamp=args.timestamp,
        copy_directory=args.copy_directory,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Distribute Python scripts to Windows machines without freezing them. The "
            "resulting distribution will be put in a folder that can be copied to any "
            'Windows machine. Users should run "<script_name>.bat" to run the script. '
            "All the dependencies, including a standalone build of Python, will be "
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
        default="requirements.txt",
        help=(
            "Path to a requirements file that lists the dependencies of the script. Defaults to"
            "'requirements.txt'."
        ),
    )
    parser.add_argument(
        "-p",
        "--python-version",
        "--python",
        default="3.13.11",
        help=(
            "Python version, in X.Y.Z format, that the distribution should use. The version must "
            "be available on https://github.com/astral-sh/python-build-standalone/releases. "
            "Defaults to 3.13.11."
        ),
    )
    parser.add_argument(
        "-t",
        "--timestamp",
        default="20251205",
        help=(
            "Release timestamp (YYYYMMDD format) for the Python build. Check "
            "https://github.com/astral-sh/python-build-standalone/releases for available dates. "
            "Defaults to 20251205."
        ),
    )
    parser.add_argument(
        "--copy-directory",
        action="store_true",
        help="Copy the contents of the script directory to the distribution.",
    )
    args = parser.parse_args()
    create_frigobar(args)


if __name__ == "__main__":
    main()
