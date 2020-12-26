import pytest
from gidpublish.utility.gidtools_functions import pathmaker, readit
import os
from gidpublish.dependencies_tool import DependencyFinder, DependencyFreezer
from gidpublish.utility.named_tuples import DependencyItem


def test_file_finding(tmp_dir_fake_package):
    dep_freezer = DependencyFreezer(tmp_dir_fake_package.get('main_path'))
    assert dep_freezer.target_dir == tmp_dir_fake_package.get('main_path')
    assert dep_freezer.project_devmeta_env_file == pathmaker(tmp_dir_fake_package.get('_project_devmeta_env_path'))

    assert dep_freezer.special_paths.get('venv_activate_script') == pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_venv', 'Scripts', 'activate.bat')
    assert dep_freezer.special_paths.get('venv_settings_folder') == pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_tools', 'venv_setup_settings')
    assert dep_freezer.special_paths.get('workspace_folder') == tmp_dir_fake_package.get('main_path')
    assert dep_freezer.special_paths.get('toplevel_module') == tmp_dir_fake_package.get('top_level_path')
    assert dep_freezer.special_paths.get('main_script_file') == pathmaker(tmp_dir_fake_package.get('top_level_path'), '__main__.py')
