import glob
import os
import shutil
from subprocess import Popen
import pathspec

BATCH_TEMPLATE = """@echo off
echo Checking uv installation...

REM Check if uv is in PATH or in the current directory
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if not exist uv.exe (
        echo uv not found. Downloading uv...
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' -OutFile 'uv.zip'; Expand-Archive 'uv.zip' -DestinationPath '.' -Force; Remove-Item 'uv.zip'"
    )
)

{pythonpath}
{env_vars}
echo Running script...
REM If downloaded locally, use .\\uv.exe, otherwise try system uv
if exist uv.exe (
    set UV_CMD=.\\uv.exe
) else (
    set UV_CMD=uv
)

if exist requirements.txt (
    if not exist .venv (
        echo Creating virtual environment...
        %UV_CMD% venv {python_arg}
    )
    echo Installing dependencies...
    %UV_CMD% pip install -r requirements.txt
)

%UV_CMD% run {run_suffix}
pause
"""


def create_frigobar(
    script_path: str,
    target_directory: str = "frigobar",
    pyproject_file: str = None,
    requirements_file: str = None,
    python_version: str = None,
    copy_directory: bool = False,
    include_directory: str = None,
    env_vars: dict = None,
    run_template: str = None,
):
    if python_version and not requirements_file:
        raise Exception("python_version can only be used when requirements_file is specified")
    if requirements_file and pyproject_file:
        raise Exception("requirements_file and pyproject_file cannot be used together")
    if copy_directory and include_directory:
        raise Exception("copy_directory and include_directory cannot be used together")

    script_path = os.path.abspath(script_path)
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)
    elif not os.path.isdir(target_directory):
        raise Exception("Target directory must be a directory")
    elif os.listdir(target_directory):
        raise Exception("Target directory must be empty")
    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        raise Exception(f"Missing script: {script_path}")

    target_directory = os.path.abspath(target_directory)

    if requirements_file:
        requirements_file = os.path.abspath(requirements_file)
        if not os.path.exists(requirements_file) or not os.path.isfile(requirements_file):
            raise Exception(f"Missing requirements file: {requirements_file}")

    if pyproject_file:
        pyproject_file = os.path.abspath(pyproject_file)
        if not os.path.exists(pyproject_file) or not os.path.isfile(pyproject_file):
            raise Exception(f"Missing pyproject file: {pyproject_file}")

    # Add a copy of the script to frigobar
    script_dir = os.path.join(target_directory, "script")
    os.mkdir(script_dir)

    def create_ignore_patterns(base_dir):
        def ignore_patterns(dir, contents):
            # Always ignore the target directory
            ignored = [c for c in contents if os.path.join(dir, c) == target_directory]

            # Apply .gitignore patterns if available
            if gitignore_spec:
                # Calculate relative path from base_dir
                rel_dir = os.path.relpath(dir, base_dir)
                if rel_dir == ".":
                    rel_dir = ""

                for item in contents:
                    if item in ignored:
                        continue

                    # Build the relative path for this item
                    if rel_dir:
                        item_path = os.path.join(rel_dir, item)
                    else:
                        item_path = item

                    # Check if item is a directory (need to append / for directory patterns)
                    full_item_path = os.path.join(dir, item)
                    if os.path.isdir(full_item_path):
                        # Check both with and without trailing slash
                        if gitignore_spec.match_file(item_path) or gitignore_spec.match_file(
                            item_path + "/"
                        ):
                            ignored.append(item)
                    else:
                        if gitignore_spec.match_file(item_path):
                            ignored.append(item)

            return ignored

        return ignore_patterns

    if include_directory:
        include_directory = os.path.abspath(include_directory)
        if not os.path.exists(include_directory) or not os.path.isdir(include_directory):
            raise Exception(
                f"Include directory does not exist or is not a directory: {include_directory}"
            )

        # Load .gitignore patterns if the file exists
        gitignore_path = os.path.join(include_directory, ".gitignore")
        gitignore_spec = None
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

        ignore_patterns = create_ignore_patterns(include_directory)

        shutil.copytree(
            include_directory,
            script_dir,
            dirs_exist_ok=True,
            ignore=ignore_patterns,
        )
    elif copy_directory:
        source_dir = os.path.dirname(script_path)

        # Load .gitignore patterns if the file exists
        gitignore_path = os.path.join(source_dir, ".gitignore")
        gitignore_spec = None
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

        ignore_patterns = create_ignore_patterns(source_dir)

        shutil.copytree(
            source_dir,
            script_dir,
            dirs_exist_ok=True,
            ignore=ignore_patterns,
        )
    else:
        shutil.copy(script_path, script_dir)

    # Handle dependencies
    if requirements_file:
        # If requirements file is provided, copy it to the root of the distribution
        shutil.copy(requirements_file, os.path.join(target_directory, "requirements.txt"))
    elif pyproject_file:
        # If pyproject file is explicitly provided, copy it to the root of the distribution
        shutil.copy(pyproject_file, os.path.join(target_directory, "pyproject.toml"))
    else:
        # If no requirements file or explicit pyproject file, try to find pyproject.toml in script directory
        pyproject_path = os.path.join(os.path.dirname(script_path), "pyproject.toml")
        if os.path.exists(pyproject_path):
            shutil.copy(pyproject_path, target_directory)

    # Create bat file
    if include_directory:
        # Calculate relative path from include_directory to script
        rel_script_path = os.path.relpath(script_path, include_directory)
        rel_script_path = os.path.join("script", rel_script_path)
    else:
        rel_script_path = os.path.join("script", os.path.basename(script_path))

    script_basename = os.path.splitext(os.path.basename(script_path))[0]
    bat_file = os.path.join(target_directory, f"{script_basename}.bat")

    python_arg = f"--python {python_version}" if python_version else ""

    # Determine the run suffix
    if run_template:
        script_quoted = f'"{rel_script_path}"'
        template_formatted = run_template.replace("{script}", script_quoted)
        run_suffix = f'{python_arg} {template_formatted}'
    else:
        run_suffix = f'{python_arg} "{rel_script_path}"'

    # Format environment variables for batch file
    # Escape special batch file characters to prevent injection
    def escape_batch_value(value: str) -> str:
        """Escape special characters in batch file values"""
        # Escape special batch characters: %, ^, &, |, <, >, (, )
        # % needs to be doubled (%%)
        # Other characters need to be prefixed with ^
        value = value.replace("%", "%%")
        for char in "^&|<>()":
            value = value.replace(char, f"^{char}")
        return value

    env_vars_str = ""
    if env_vars:
        for key, value in env_vars.items():
            escaped_value = escape_batch_value(value)
            env_vars_str += f"set {key}={escaped_value}\n"

    pythonpath_str = ""
    if include_directory:
        # Set PYTHONPATH to the script directory so modules can be imported
        pythonpath_str = 'set "PYTHONPATH=%~dp0script"\n'

    with open(bat_file, "w") as f:
        f.write(
            BATCH_TEMPLATE.format(
                python_arg=python_arg,
                script_path=rel_script_path,
                pythonpath=pythonpath_str,
                env_vars=env_vars_str,
                run_suffix=run_suffix,
            )
        )


def fill_frigobar(frigobar_path: str):
    bat_pattern = os.path.join(frigobar_path, "*.bat")
    bat_file = glob.glob(bat_pattern)[0]
    p = Popen(bat_file)
    stdout, stderr = p.communicate()
