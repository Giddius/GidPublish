import pytest
from gidpublish.version_tools.version_handling import VersionManager
import os
from gidpublish.utility.gidtools_functions import readit


def test_version_manager_overall(fake_package_path, fake_package_init_content):
    version_manager = VersionManager(fake_package_path)
    assert readit(version_manager.version_file) == fake_package_init_content
    assert str(version_manager.version) == "0.1.1"
    version_manager.increment_version(VersionManager.MAJOR)
    assert str(version_manager.version) == "1.0.0"
    version_manager.set(VersionManager.PATCH, 9)
    assert str(version_manager.version) == "1.0.9"
    new_version_manager = VersionManager(fake_package_path)
    assert str(new_version_manager.version) == "1.0.9"


def test_version_manager_no_auto_write(fake_package_path, fake_package_init_content):
    VersionManager.set_auto_write(False)
    version_manager = VersionManager(fake_package_path)
    assert readit(version_manager.version_file) == fake_package_init_content
    assert str(version_manager.version) == "0.1.1"
    version_manager.increment_version(VersionManager.MAJOR)
    assert str(version_manager.version) == "1.0.0"
    new_version_manager = VersionManager(fake_package_path)
    assert str(new_version_manager.version) == "0.1.1"
    version_manager.write()
    new_version_manager = VersionManager(fake_package_path)
    assert str(new_version_manager.version) == "1.0.0"
