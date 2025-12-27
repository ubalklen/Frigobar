import os
import shutil
from os import path

import pytest

from frigobar import frigobar

test_dir = path.dirname(__file__)
target_dir = path.join(test_dir, "test_frigobar")
script_path = path.join(test_dir, "script_folder", "script.py")
requirements_file = path.join(test_dir, "script_folder", "requirements.txt")
python_version = "3.8.5"


@pytest.fixture(autouse=True)
def delete_test_frigobar():
    shutil.rmtree(target_dir, ignore_errors=True)
    yield
    shutil.rmtree(target_dir, ignore_errors=True)


@pytest.fixture
def target_dir_inside_script_dir():
    new_target_dir = path.join(test_dir, "script_folder", "test_frigobar")
    shutil.rmtree(new_target_dir, ignore_errors=True)
    yield new_target_dir
    shutil.rmtree(new_target_dir, ignore_errors=True)


def test_create_frigobar_with_requirements():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "requirements.txt"))
    assert not path.exists(path.join(target_dir, "pyproject.toml"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        assert "pip install -r requirements.txt" in content
        assert f'run --python {python_version} "script\\script.py"' in content


def test_create_frigobar_with_pyproject():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=None,
        python_version=None,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert not path.exists(path.join(target_dir, "requirements.txt"))
    assert path.exists(path.join(target_dir, "pyproject.toml"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        # The command is present in the template but guarded by 'if exist requirements.txt'
        assert 'run  "script\\script.py"' in content


def test_create_frigobar_rel_script_path():
    original_cwd = os.getcwd()
    try:
        os.chdir(os.path.dirname(script_path))
        script_rel_path = os.path.basename(script_path)
        frigobar.create_frigobar(
            script_path=script_rel_path,
            target_directory=target_dir,
            requirements_file=None,
            python_version=None,
        )

        assert path.exists(path.join(target_dir, "script", "script.py"))
        assert path.exists(path.join(target_dir, "pyproject.toml"))
        assert path.exists(path.join(target_dir, "script.bat"))
    finally:
        os.chdir(original_cwd)


def test_create_frigobar_copy_script_dir():
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=None,
        python_version=None,
        copy_directory=True,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "another_script.py"))
    # data directory is now ignored by .gitignore
    assert not path.exists(path.join(target_dir, "script", "data"))
    assert path.exists(path.join(target_dir, "pyproject.toml"))
    assert path.exists(path.join(target_dir, "script.bat"))


def test_create_frigobar_target_dir_inside_script_dir(target_dir_inside_script_dir):
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir_inside_script_dir,
        requirements_file=None,
        python_version=None,
        copy_directory=True,
    )

    assert path.exists(path.join(target_dir_inside_script_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir_inside_script_dir, "script.bat"))


def test_create_frigobar_python_version_without_requirements_raises():
    with pytest.raises(Exception) as excinfo:
        frigobar.create_frigobar(
            script_path=script_path,
            target_directory=target_dir,
            requirements_file=None,
            python_version="3.12",
        )
    assert "python_version can only be used when requirements_file is specified" in str(
        excinfo.value
    )


def test_create_frigobar_copy_directory_honors_gitignore():
    """Test that --copy-directory honors .gitignore patterns"""
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=None,
        python_version=None,
        copy_directory=True,
    )

    # Files that should be copied
    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert path.exists(path.join(target_dir, "script", "another_script.py"))
    
    # Directory that should be ignored according to .gitignore
    assert not path.exists(path.join(target_dir, "script", "data"))
    
    # .gitignore itself should be copied
    assert path.exists(path.join(target_dir, "script", ".gitignore"))
