from contextlib import contextmanager
import shlex
import os
import sys
import subprocess
import yaml
import datetime
import tempfile
import shutil
from cookiecutter.main import cookiecutter

@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)

@contextmanager
def bake_in_temp_dir(template_path, extra_context=None, keep_temp_dir=False):
    """
    Bake a cookiecutter template in a temporary directory.
    :param template_path: Path to the cookiecutter template.
    :param extra_context: Additional context for cookiecutter.
    :param keep_temp_dir: Boolean, if True, the temporary directory will not be removed.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        cookiecutter(template_path, no_input=True, extra_context=extra_context, output_dir=temp_dir)
        yield temp_dir
    finally:
        if not keep_temp_dir:
            shutil.rmtree(temp_dir)

def test_bake_with_defaults():
    template_path = os.path.abspath("../cookiecutter-pypackage")
    with bake_in_temp_dir(template_path) as temp_dir:
        project_dir = os.path.join(temp_dir, 'python-boilerplate')
        project_files = os.listdir(project_dir)
        assert 'pyproject.toml' in project_files
        assert 'README.md' in project_files
        assert 'tests' in project_files

def test_bake_and_run_tests():
    template_path = os.path.abspath("../cookiecutter-pypackage")
    with bake_in_temp_dir(template_path) as temp_dir:
        assert os.path.isdir(temp_dir)

        # Check that pytest is used by default
        test_file_path = os.path.join(temp_dir, 'python-boilerplate', 'tests', 'test_python_boilerplate.py')
        with open(test_file_path, 'r') as test_file:
            assert "import pytest" in test_file.read()

        # Run pytest directly to validate the baked project
        result = subprocess.run(['pytest', '--maxfail=1', '--disable-warnings'], cwd=temp_dir, capture_output=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
        assert result.returncode == 0

def test_bake_with_custom_context():
    template_path = os.path.abspath("../cookiecutter-pypackage")
    extra_context = {
        "project_name": "Custom Project",
        "full_name": "Test Author",
        "package_name": "custom-project",
        "project_slug": "custom_project",
        "repository_name": "custom-project"
    }
    with bake_in_temp_dir(template_path, extra_context=extra_context) as temp_dir:
        project_dir = os.path.join(temp_dir, 'custom-project')
        with open(os.path.join(project_dir, 'pyproject.toml')) as f:
            content = f.read()
            assert "Custom Project" in content
            assert "Test Author" in content

def test_year_in_license_file():
    """Ensure the current year is included in the LICENSE file."""
    template_path = os.path.abspath("../cookiecutter-pypackage")
    with bake_in_temp_dir(template_path) as temp_dir:
        license_file_path = os.path.join(temp_dir, 'python-boilerplate', 'LICENSE')
        now = datetime.datetime.now()
        with open(license_file_path, 'r') as license_file:
            assert str(now.year) in license_file.read()

def test_bake_with_special_characters():
    """Ensure special characters in `full_name` do not break the template."""
    template_path = os.path.abspath("../cookiecutter-pypackage")
    extra_context = {"full_name": "O'Connor"}
    with bake_in_temp_dir(template_path, extra_context=extra_context) as temp_dir:
        project_dir = os.path.join(temp_dir, 'python-boilerplate')
        assert os.path.isdir(project_dir)

def test_bake_with_custom_context_license_owner():
    """Test license owner logic based on GitHub ownership."""
    template_path = os.path.abspath("../cookiecutter-pypackage")

    # Case 1: User is the owner
    extra_context_owner = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "github_username": "testuser",
        "github_owner": "testuser"
    }
    with bake_in_temp_dir(template_path, extra_context=extra_context_owner) as temp_dir:
        license_file_path = os.path.join(temp_dir, 'python-boilerplate', 'LICENSE')
        with open(license_file_path, 'r') as license_file:
            content = license_file.read()
            assert "Test User" in content

    # Case 2: User is not the owner
    extra_context_not_owner = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "github_username": "testuser",
        "github_owner": "DAI-Lab"
    }
    with bake_in_temp_dir(template_path, extra_context=extra_context_not_owner) as temp_dir:
        license_file_path = os.path.join(temp_dir, 'python-boilerplate', 'LICENSE')
        with open(license_file_path, 'r') as license_file:
            content = license_file.read()
            assert "MIT Data To AI Lab" in content
