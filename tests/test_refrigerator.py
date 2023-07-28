import os
import shutil
from os import path

import pytest

from refrigerator import refrigerator

test_dir = path.dirname(__file__)
target_dir = path.join(test_dir, "test_refrigerator")
downloaders_dir = path.join(path.dirname(test_dir), "refrigerator", "downloaders")
script_path = path.join(test_dir, "script_folder", "script.py")
requirements_file = path.join(test_dir, "script_folder", "requirements.txt")
python_version = "3.8.5"
use_proxy = True  # TODO: check when proxy is needed


@pytest.fixture(autouse=True)
def delete_test_refrigerator():
    shutil.rmtree(target_dir, ignore_errors=True)
    yield
    shutil.rmtree(target_dir, ignore_errors=True)


def test_create_simple_refrigerator():
    refrigerator.create_refrigerator(
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


def test_create_refrigerator_with_folder():
    refrigerator.create_refrigerator(
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


def test_fill_refrigerator():
    refrigerator.create_refrigerator(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        use_proxy=use_proxy,
    )
    refrigerator.fill_refrigerator(refrigerator_path=target_dir)
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
