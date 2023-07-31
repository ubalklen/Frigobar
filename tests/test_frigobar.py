import os
import shutil
from os import path

import pytest

from frigobar import frigobar

test_dir = path.dirname(__file__)
target_dir = path.join(test_dir, "test_frigobar")
downloaders_dir = path.join(path.dirname(test_dir), "frigobar", "downloaders")
script_path = path.join(test_dir, "script_folder", "script.py")
requirements_file = path.join(test_dir, "script_folder", "requirements.txt")
python_version = "3.8.5"


@pytest.fixture(autouse=True)
def delete_test_frigobar():
    shutil.rmtree(target_dir, ignore_errors=True)
    yield
    shutil.rmtree(target_dir, ignore_errors=True)


def test_create_frigobar_abs_script_path():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "requirements.txt"))
    assert path.exists(path.join(target_dir, "downloaders", "download_python.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_pip.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_deps.ps1"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        assert (
            f.read()
            == r'''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version 3.8.5 -TargetDirectory "."
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "python-3.8.5-embed-amd64"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "script\requirements.txt" -PipPath "python-3.8.5-embed-amd64\Scripts\pip.exe"
"%~dp0/python-3.8.5-embed-amd64/python.exe" "script\script.py"'''
        )


def test_create_frigobar_rel_script_path():
    os.chdir(os.path.dirname(script_path))
    script_rel_path = os.path.basename(script_path)
    frigobar.create_frigobar(
        script_path=script_rel_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "requirements.txt"))
    assert path.exists(path.join(target_dir, "downloaders", "download_python.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_pip.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_deps.ps1"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        assert (
            f.read()
            == r'''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version 3.8.5 -TargetDirectory "."
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "python-3.8.5-embed-amd64"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "script\requirements.txt" -PipPath "python-3.8.5-embed-amd64\Scripts\pip.exe"
"%~dp0/python-3.8.5-embed-amd64/python.exe" "script\script.py"'''
        )


def test_create_frigobar_with_folder():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        copy_directory=True,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "another_script.py"))
    assert path.exists(path.join(target_dir, "script", "data"))
    assert path.exists(path.join(target_dir, "script", "data", "data"))
    assert path.exists(path.join(target_dir, "script", "requirements.txt"))
    assert path.exists(path.join(target_dir, "downloaders", "download_python.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_pip.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_deps.ps1"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        assert (
            f.read()
            == r'''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version 3.8.5 -TargetDirectory "."
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "python-3.8.5-embed-amd64"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "script\requirements.txt" -PipPath "python-3.8.5-embed-amd64\Scripts\pip.exe"
"%~dp0/python-3.8.5-embed-amd64/python.exe" "script\script.py"'''
        )


def test_create_frigobar_with_folder_and_rel_script_path():
    os.chdir(os.path.dirname(script_path))
    script_rel_path = os.path.basename(script_path)
    frigobar.create_frigobar(
        script_path=script_rel_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        copy_directory=True,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "another_script.py"))
    assert path.exists(path.join(target_dir, "script", "data"))
    assert path.exists(path.join(target_dir, "script", "data", "data"))
    assert path.exists(path.join(target_dir, "script", "requirements.txt"))
    assert path.exists(path.join(target_dir, "downloaders", "download_python.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_pip.ps1"))
    assert path.exists(path.join(target_dir, "downloaders", "download_deps.ps1"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        assert (
            f.read()
            == r'''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version 3.8.5 -TargetDirectory "."
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_pip.ps1" -TargetDirectory "python-3.8.5-embed-amd64"
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_deps.ps1" -RequirementsFile "script\requirements.txt" -PipPath "python-3.8.5-embed-amd64\Scripts\pip.exe"
"%~dp0/python-3.8.5-embed-amd64/python.exe" "script\script.py"'''
        )


def test_create_frigobar_without_reqs():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=None,
        python_version=python_version,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "downloaders", "download_python.ps1"))
    assert path.exists(path.join(target_dir, "script.bat"))
    assert not path.exists(path.join(target_dir, "script", "requirements.txt"))
    assert not path.exists(path.join(target_dir, "downloaders", "download_pip.ps1"))
    assert not path.exists(path.join(target_dir, "downloaders", "download_deps.ps1"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        assert (
            f.read()
            == r'''powershell Unblock-File -Path '%~dp0downloaders\download_python.ps1'
powershell -ExecutionPolicy Bypass -File "%~dp0downloaders\download_python.ps1" -Version 3.8.5 -TargetDirectory "."
"%~dp0/python-3.8.5-embed-amd64/python.exe" "script\script.py"'''
        )


def test_fill_frigobar():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
    )
    frigobar.fill_frigobar(frigobar_path=target_dir)
    assert path.exists(path.join(target_dir, f"python-{python_version}-embed-amd64"))
    assert path.exists(
        path.join(
            target_dir,
            f"python-{python_version}-embed-amd64",
            "Lib",
            "site-packages",
            "requests",
        )
    )
