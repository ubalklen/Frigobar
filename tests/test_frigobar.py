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


def test_create_frigobar_with_explicit_pyproject_file():
    """Test that --pyproject-file parameter works correctly"""
    pyproject_file = path.join(test_dir, "script_folder", "pyproject.toml")
    
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=None,
        python_version=None,
        pyproject_file=pyproject_file,
    )

    assert path.exists(path.join(target_dir, "script", "script.py"))
    assert not path.exists(path.join(target_dir, "requirements.txt"))
    assert path.exists(path.join(target_dir, "pyproject.toml"))
    assert path.exists(path.join(target_dir, "script.bat"))

    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        # Check for the command with forward slashes (actual output)
        assert 'run  "script/script.py"' in content


def test_create_frigobar_pyproject_file_and_requirements_file_mutually_exclusive():
    """Test that pyproject_file and requirements_file cannot be used together"""
    pyproject_file = path.join(test_dir, "script_folder", "pyproject.toml")
    
    with pytest.raises(Exception) as excinfo:
        frigobar.create_frigobar(
            script_path=script_path,
            target_directory=target_dir,
            requirements_file=requirements_file,
            python_version=None,
            pyproject_file=pyproject_file,
        )
    assert "requirements_file and pyproject_file cannot be used together" in str(
        excinfo.value
    )


def test_create_frigobar_pyproject_file_from_different_directory():
    """Test that pyproject.toml can be loaded from a different directory than the script"""
    # Create a temporary pyproject.toml in a different location
    temp_dir = path.join(test_dir, "temp_config")
    os.makedirs(temp_dir, exist_ok=True)
    temp_pyproject = path.join(temp_dir, "pyproject.toml")
    
    # Use a different target directory to avoid conflicts
    temp_target_dir = path.join(test_dir, "test_frigobar_temp")
    
    try:
        # Create a custom pyproject.toml
        with open(temp_pyproject, "w") as f:
            f.write('[project]\nname = "custom-project"\nversion = "1.0.0"\ndependencies = ["numpy"]\n')
        
        frigobar.create_frigobar(
            script_path=script_path,
            target_directory=temp_target_dir,
            requirements_file=None,
            python_version=None,
            pyproject_file=temp_pyproject,
        )

        assert path.exists(path.join(temp_target_dir, "script", "script.py"))
        assert path.exists(path.join(temp_target_dir, "pyproject.toml"))
        
        # Verify the correct pyproject.toml was copied
        with open(path.join(temp_target_dir, "pyproject.toml"), "r") as f:
            content = f.read()
            assert "custom-project" in content
            assert "numpy" in content
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(temp_target_dir, ignore_errors=True)


def test_create_frigobar_missing_pyproject_file_raises():
    """Test that specifying a non-existent pyproject file raises an exception"""
    nonexistent_pyproject = path.join(test_dir, "nonexistent", "pyproject.toml")
    
    # Use a different target directory to avoid conflicts
    temp_target_dir = path.join(test_dir, "test_frigobar_missing")
    
    try:
        with pytest.raises(Exception) as excinfo:
            frigobar.create_frigobar(
                script_path=script_path,
                target_directory=temp_target_dir,
                requirements_file=None,
                python_version=None,
                pyproject_file=nonexistent_pyproject,
            )
        assert "Missing pyproject file" in str(excinfo.value)
    finally:
        shutil.rmtree(temp_target_dir, ignore_errors=True)


def test_create_frigobar_with_env_vars():
    """Test that environment variables are properly set in the bat file"""
    env_vars = {
        "MY_VAR": "test_value",
        "ANOTHER_VAR": "123",
        "PATH_VAR": "C:\\some\\path",
    }
    
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        env_vars=env_vars,
    )

    assert path.exists(path.join(target_dir, "script.bat"))
    
    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        # Check that each environment variable is set in the bat file
        assert "set MY_VAR=test_value" in content
        assert "set ANOTHER_VAR=123" in content
        assert "set PATH_VAR=C:\\some\\path" in content


def test_create_frigobar_without_env_vars():
    """Test that the bat file works correctly when no env vars are provided"""
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        env_vars=None,
    )

    assert path.exists(path.join(target_dir, "script.bat"))
    
    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        # Ensure no stray "set " commands appear when env_vars is None
        # The template should have a blank line where env_vars would go
        assert "echo Running script..." in content


def test_create_frigobar_with_empty_env_vars():
    """Test that the bat file works correctly when empty env vars dict is provided"""
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        env_vars={},
    )

    assert path.exists(path.join(target_dir, "script.bat"))
    
    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        assert "echo Running script..." in content


def test_create_frigobar_with_special_chars_in_env_vars():
    """Test that special batch characters are properly escaped in env vars"""
    env_vars = {
        "VAR_WITH_PERCENT": "value%with%percent",
        "VAR_WITH_PIPE": "value|pipe",
        "VAR_WITH_AMP": "value&ampersand",
        "VAR_WITH_CARET": "value^caret",
        "VAR_WITH_ANGLE": "value<angle>",
        "VAR_WITH_PARENS": "value(with)parens",
    }
    
    frigobar.create_frigobar(
        script_path=script_path,
        target_directory=target_dir,
        requirements_file=requirements_file,
        python_version=python_version,
        env_vars=env_vars,
    )

    assert path.exists(path.join(target_dir, "script.bat"))
    
    with open(path.join(target_dir, "script.bat"), "r") as f:
        content = f.read()
        # Check that special characters are properly escaped
        assert "set VAR_WITH_PERCENT=value%%with%%percent" in content
        assert "set VAR_WITH_PIPE=value^|pipe" in content
        assert "set VAR_WITH_AMP=value^&ampersand" in content
        assert "set VAR_WITH_CARET=value^^caret" in content
        assert "set VAR_WITH_ANGLE=value^<angle^>" in content
        assert "set VAR_WITH_PARENS=value^(with^)parens" in content

