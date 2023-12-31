import glob
import os
import shutil
from subprocess import Popen

unblock_cmd = "powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'"
download_python_cmd = 'powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version {python_version} -TargetDirectory "{rel_target_directory}"'
download_pip_cmd = 'powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "{rel_python_directory}"'
download_deps_cmd = 'powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "{rel_requirements_file}" -PipPath "{rel_pip_path}"'
download_tkinter_cmd = 'powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_tkinter.ps1" -TargetDirectory "{rel_target_directory}" -PythonVersion {python_version} -MoveFiles -PythonDirectory "{rel_python_directory}"'
run_script_cmd = (
    '"%~dp0/python-{python_version}-embed-amd64/python.exe" "{rel_script_path}"'
)


def create_frigobar(
    script_path: str,
    target_directory: str = "frigobar",
    python_version: str = "3.11.4",
    requirements_file: str = None,
    copy_directory: bool = False,
    tkinter: bool = False,
):
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

    requirements_file = (
        os.path.abspath(requirements_file) if requirements_file else None
    )
    if requirements_file and (
        not os.path.exists(requirements_file) or not os.path.isfile(requirements_file)
    ):
        raise Exception(f"Missing requirements file: {requirements_file}")

    # Add a copy of the script to frigobar
    script_dir = os.path.join(target_directory, "script")
    os.mkdir(script_dir)
    if not copy_directory:
        shutil.copy(script_path, script_dir)
    else:

        def ignore_target_dir(dir, contents):
            return [c for c in contents if os.path.join(dir, c) == target_directory]

        shutil.copytree(
            os.path.dirname(script_path),
            script_dir,
            dirs_exist_ok=True,
            ignore=ignore_target_dir,
        )

    # Add a copy of the requirements file to frigobar
    if requirements_file:
        shutil.copy(requirements_file, script_dir)

    # Add a copy of the downloaders to frigobar
    downloaders_dir = os.path.join(os.path.dirname(__file__), "downloaders")
    downloader_scripts = [os.path.join(downloaders_dir, "download_python.ps1")]
    if requirements_file:
        downloader_scripts += [
            os.path.join(downloaders_dir, "download_pip.ps1"),
            os.path.join(downloaders_dir, "download_deps.ps1"),
        ]
    if tkinter:
        downloader_scripts += [
            os.path.join(downloaders_dir, "download_tkinter.ps1"),
        ]
    downloaders_dir = os.path.join(target_directory, "downloaders")
    os.mkdir(downloaders_dir)
    for script in downloader_scripts:
        if not os.path.exists(script):
            raise Exception(f"Missing script: {script}")
        shutil.copy(script, downloaders_dir)

    # Create bat file
    python_directory = os.path.join(
        target_directory, f"python-{python_version}-embed-amd64"
    )
    rel_target_directory = os.path.relpath(target_directory, target_directory)
    rel_python_directory = os.path.relpath(python_directory, target_directory)
    rel_pip_path = os.path.relpath(
        os.path.join(python_directory, "Scripts", "pip.exe"), target_directory
    )
    rel_script_path = os.path.relpath(
        os.path.join(script_dir, os.path.basename(script_path)), target_directory
    )
    if requirements_file:
        rel_requirements_file = os.path.relpath(
            os.path.join(script_dir, os.path.basename(requirements_file)),
            target_directory,
        )
    else:
        rel_requirements_file = ""
    script_basename = os.path.splitext(os.path.basename(script_path))[0]
    bat_file = os.path.join(target_directory, f"{script_basename}.bat")
    with open(bat_file, "w") as f:
        template_list = [unblock_cmd, download_python_cmd]
        if requirements_file:
            template_list.append(download_pip_cmd)
            template_list.append(download_deps_cmd)
        if tkinter:
            template_list.append(download_tkinter_cmd)
        template_list.append(run_script_cmd)
        template = "\n".join(template_list)
        f.write(
            template.format(
                python_version=python_version,
                rel_target_directory=rel_target_directory,
                rel_python_directory=rel_python_directory,
                rel_requirements_file=rel_requirements_file,
                rel_pip_path=rel_pip_path,
                rel_script_path=rel_script_path,
            )
        )

    # Add _tkinter.pyd to frigobar
    if tkinter:
        tkinter_pyd_path = os.path.join(
            os.path.dirname(__file__), "_tkinter", "_tkinter.pyd"
        )
        shutil.copy(tkinter_pyd_path, target_directory)


def fill_frigobar(frigobar_path: str):
    bat_pattern = os.path.join(frigobar_path, "*.bat")
    bat_file = glob.glob(bat_pattern)[0]
    p = Popen(bat_file)
    stdout, stderr = p.communicate()
