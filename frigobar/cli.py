import argparse

from frigobar import frigobar


def create_frigobar(args):
    frigobar.create_frigobar(
        script_path=args.script_path,
        target_directory=args.target_directory,
        pyproject_file=args.pyproject_file,
        requirements_file=args.requirements_file,
        python_version=args.python_version,
        copy_directory=args.copy_directory,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Distribute Python scripts to Windows machines without freezing them. The folder of "
            "the resulting distribution can be copied to any Windows machine. Users should run "
            '"<script_name>.bat" to run the script. All the dependencies, including Python, will '
            "be downloaded and installed on the first run."
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
        "-t",
        "--pyproject-file",
        default=None,
        help=(
            "Path to a pyproject.toml file that contains the dependencies of the script. "
            "If not provided, the tool will look for a pyproject.toml file in the script's directory. "
            "Cannot be used together with --requirements-file."
        ),
    )
    parser.add_argument(
        "-r",
        "--requirements-file",
        default=None,
        help=(
            "Path to a classical requirements file (usually called requirements.txt) that lists"
            " the dependencies of the script. If not provided, dependencies must be declared in a "
            "pyproject.toml file or inline."
        ),
    )
    parser.add_argument(
        "-p",
        "--python-version",
        "--python",
        default=None,
        help=(
            "Python version, in X.Y.Z format, that the distribution should use. Only works when "
            "--requirements-file is specified. If not provided, the latest Python supported by the"
            "final user's system will be used."
        ),
    )
    parser.add_argument(
        "--copy-directory",
        action="store_true",
        help="Copy the contents of the script directory to the distribution. Respects .gitignore if present.",
    )
    args = parser.parse_args()
    if args.python_version and not args.requirements_file:
        parser.error("--python-version requires --requirements-file to be specified.")
    if args.requirements_file and args.pyproject_file:
        parser.error("--requirements-file and --pyproject-file cannot be used together.")
    create_frigobar(args)


if __name__ == "__main__":
    main()
