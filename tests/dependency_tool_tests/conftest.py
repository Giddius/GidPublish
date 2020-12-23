import pytest
from gidpublish.dependencies_tool import DependencyFinder
from gidpublish.utility.gidtools_functions import pathmaker, writeit
import os
from tempfile import TemporaryDirectory


THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
FAKE_PACKAGE_DIR = pathmaker(THIS_FILE_DIR, 'fake_package')
FAKE_PACKAGE_TOP_MODULE = pathmaker(FAKE_PACKAGE_DIR, 'fake_gidappdata')

FAKE_PYPROJECT_STRING = """[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "fake_gidappdata"
author = "Giddius"
home-page = "https://github.com/Giddius/GidAppData"
classifiers = ["License :: OSI Approved :: MIT License"]
description-file = "readme.md"
requires = [

]

[tool.flit.scripts]

"""


@pytest.fixture()
def fake_pyproject_file():
    with TemporaryDirectory() as tempdir:
        path = pathmaker(tempdir, "pyproject.toml")
        writeit(path, FAKE_PYPROJECT_STRING)
        yield path, FAKE_PYPROJECT_STRING


@pytest.fixture()
def temp_requirement_file():
    with TemporaryDirectory() as tempdir:
        yield pathmaker(tempdir, 'requirements.txt')


@pytest.fixture()
def fake_top_module():
    return FAKE_PACKAGE_TOP_MODULE


@pytest.fixture()
def this_dir():
    return pathmaker(THIS_FILE_DIR)


@pytest.fixture()
def fake_package_dir():
    return FAKE_PACKAGE_DIR


@pytest.fixture()
def dep_finder(fake_top_module):
    return DependencyFinder(fake_top_module)
