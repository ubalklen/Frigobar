import glob
import os
import shutil
from subprocess import Popen

BAT_TEMPLATE = '''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version {python_version} -TargetDirectory "{rel_target_directory}"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "{rel_python_directory}"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "{rel_requirements_file}" -PipPath "{rel_pip_path}"
"%~dp0/python-{python_version}-embed-amd64/python.exe" "{rel_script_path}"'''
BAT_TEMPLATE_NO_REQ = '''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version {python_version} -TargetDirectory "{rel_target_directory}"
"%~dp0python-{python_version}-embed-amd64/python.exe" "{rel_script_path}"'''


def create_refrigerator(
    script_path: str,
    target_directory: str = "refrigerator",
    python_version: str = "3.11.4",
    requirements_file: str = None,
    copy_directory: bool = False,
):
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)
    elif not os.path.isdir(target_directory):
        raise Exception("Target directory must be a directory")
    elif os.listdir(target_directory):
        raise Exception("Target directory must be empty")
    python_directory = os.path.join(
        target_directory, f"python-{python_version}-embed-amd64"
    )

    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        raise Exception(f"Missing script: {script_path}")

    if requirements_file and (
        not os.path.exists(requirements_file) or not os.path.isfile(requirements_file)
    ):
        raise Exception(f"Missing requirements file: {requirements_file}")

    # Add a copy of the script to refrigerator
    script_dir = os.path.join(target_directory, "script")
    os.mkdir(script_dir)
    if not copy_directory:
        shutil.copy(script_path, script_dir)
    else:
        shutil.copytree(os.path.dirname(script_path), script_dir, dirs_exist_ok=True)

    # Add a copy of the requirements file to refrigerator
    if requirements_file:
        shutil.copy(requirements_file, script_dir)

    # Add a copy of the downloaders to refrigerator
    downloaders_dir = os.path.join(os.path.dirname(__file__), "downloaders")
    downloader_scripts = (
        [
            os.path.join(downloaders_dir, "download_python.ps1"),
            os.path.join(downloaders_dir, "download_pip.ps1"),
            os.path.join(downloaders_dir, "download_deps.ps1"),
        ]
        if requirements_file
        else [
            os.path.join(downloaders_dir, "download_python.ps1"),
        ]
    )
    downloaders_dir = os.path.join(target_directory, "downloaders")
    os.mkdir(downloaders_dir)
    for script in downloader_scripts:
        if not os.path.exists(script):
            raise Exception(f"Missing script: {script}")
        shutil.copy(script, downloaders_dir)

    # Create bat file
    rel_target_directory = os.path.relpath(target_directory, target_directory)
    rel_python_directory = os.path.relpath(python_directory, target_directory)
    rel_requirements_file = os.path.relpath(
        os.path.join(script_dir, os.path.basename(requirements_file)), target_directory
    )
    rel_pip_path = os.path.relpath(
        os.path.join(python_directory, "Scripts", "pip.exe"), target_directory
    )
    rel_script_path = os.path.relpath(
        os.path.join(script_dir, os.path.basename(script_path)), target_directory
    )
    script_basename = os.path.splitext(os.path.basename(script_path))[0]
    bat_file = os.path.join(target_directory, f"{script_basename}.bat")
    with open(bat_file, "w") as f:
        if requirements_file:
            f.write(
                BAT_TEMPLATE.format(
                    python_version=python_version,
                    rel_target_directory=rel_target_directory,
                    rel_python_directory=rel_python_directory,
                    rel_requirements_file=rel_requirements_file,
                    rel_pip_path=rel_pip_path,
                    rel_script_path=rel_script_path,
                )
            )
        else:
            f.write(
                BAT_TEMPLATE_NO_REQ.format(
                    python_version=python_version,
                    rel_target_directory=rel_target_directory,
                    rel_python_directory=rel_python_directory,
                    rel_script_path=rel_script_path,
                )
            )


def fill_refrigerator(refrigerator_path: str):
    bat_pattern = os.path.join(refrigerator_path, "*.bat")
    bat_file = glob.glob(bat_pattern)[0]
    p = Popen(bat_file)
    stdout, stderr = p.communicate()
