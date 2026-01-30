import argparse
import os

from frigobar import frigobar


def create_frigobar(args):
    # Parse environment variables from the --env-var argument
    env_vars = {}
    if args.env_var:
        for env_pair in args.env_var:
            if "=" not in env_pair:
                raise ValueError(
                    f"Invalid environment variable format: {env_pair}. Expected KEY=VALUE"
                )
            key, value = env_pair.split("=", 1)
            env_vars[key] = value

    frigobar.create_frigobar(
        script_path=args.script_path,
        target_directory=args.target_directory,
        pyproject_file=args.pyproject_file,
        requirements_file=args.requirements_file,
        python_version=args.python_version,
        copy_directory=args.copy_directory,
        include_directory=args.include_directory,
        env_vars=env_vars if env_vars else None,
        run_template=args.run_template,
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
    parser.add_argument(
        "--include-directory",
        default=None,
        help=(
            "Copy the specified directory to the distribution. The script must be located inside this directory (or in a subdirectory). "
            "Respects .gitignore if present. Cannot be used together with --copy-directory."
        ),
    )
    parser.add_argument(
        "-e",
        "--env-var",
        action="append",
        default=None,
        dest="env_var",
        help=(
            "Set environment variables in the generated batch file. "
            "Format: KEY=VALUE. Can be used multiple times to set multiple variables. "
            "Example: --env-var MY_VAR=value --env-var ANOTHER_VAR=123"
        ),
    )
    parser.add_argument(
        "--run-template",
        default=None,
        help=(
            "Custom template for the run command in the batch file. Use {script} as a placeholder for the script path. "
            "The template will be used as the argument to 'uv run'. If not provided, defaults to '{script}'. "
            "Example: --run-template 'streamlit run {script} --server.port 8501'"
        ),
    )
    args = parser.parse_args()
    if args.python_version and not args.requirements_file:
        parser.error("--python-version requires --requirements-file to be specified.")
    if args.requirements_file and args.pyproject_file:
        parser.error("--requirements-file and --pyproject-file cannot be used together.")
    if args.copy_directory and args.include_directory:
        parser.error("--copy-directory and --include-directory cannot be used together.")
    if args.include_directory:
        include_dir = os.path.abspath(args.include_directory)
        script_dir = os.path.abspath(args.script_path)
        if not os.path.commonpath([include_dir]) == os.path.commonpath([include_dir, script_dir]):
            parser.error("The script must be located inside the --include-directory.")
    create_frigobar(args)


if __name__ == "__main__":
    main()
