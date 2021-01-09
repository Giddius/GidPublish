import pytest
from gidpublish.utility.gidtools_functions import pathmaker, readit
import os
from gidpublish.dependencies_tool import DependencyFinder, DependencyFreezer
from gidpublish.utility.named_tuples import DependencyItem
from textwrap import dedent


def test_file_finding(tmp_dir_fake_package):
    dep_freezer = DependencyFreezer(tmp_dir_fake_package.get('main_path'))
    assert dep_freezer.target_dir == tmp_dir_fake_package.get('main_path')
    assert dep_freezer.project_devmeta_env_file == pathmaker(tmp_dir_fake_package.get('_project_devmeta_env_path'))

    assert dep_freezer.special_paths.get('venv_activate_script') == pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_venv', 'Scripts', 'activate.bat')
    assert dep_freezer.special_paths.get('venv_settings_folder') == pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_tools', 'venv_setup_settings')
    assert dep_freezer.special_paths.get('workspace_folder') == tmp_dir_fake_package.get('main_path')
    assert dep_freezer.special_paths.get('toplevel_module') == tmp_dir_fake_package.get('top_level_path')
    assert dep_freezer.special_paths.get('main_script_file') == pathmaker(tmp_dir_fake_package.get('top_level_path'), '__main__.py')


def test_venv_settings_files(tmp_dir_fake_package):
    dep_freezer = DependencyFreezer(tmp_dir_fake_package.get('main_path'))
    assert set(map(lambda x: x.name, dep_freezer.venv_settings_files)) == {"post_setup_scripts.txt",
                                                                           "pre_setup_scripts.txt",
                                                                           "required_dev.txt",
                                                                           "required_from_github.txt",
                                                                           "required_misc.txt",
                                                                           "required_personal_packages.txt",
                                                                           "required_qt.txt",
                                                                           "required_test.txt"}

    os.remove(pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_tools', 'venv_setup_settings', 'required_dev.txt'))

    assert set(map(lambda x: x.name, dep_freezer.venv_settings_files)) == {"post_setup_scripts.txt",
                                                                           "pre_setup_scripts.txt",
                                                                           "required_from_github.txt",
                                                                           "required_misc.txt",
                                                                           "required_personal_packages.txt",
                                                                           "required_qt.txt",
                                                                           "required_test.txt"}
    dep_freezer.ensure_mandatory_files()
    assert set(map(lambda x: x.name, dep_freezer.venv_settings_files)) == {"post_setup_scripts.txt",
                                                                           "pre_setup_scripts.txt",
                                                                           "required_dev.txt",
                                                                           "required_from_github.txt",
                                                                           "required_misc.txt",
                                                                           "required_personal_packages.txt",
                                                                           "required_qt.txt",
                                                                           "required_test.txt"}

    assert pathmaker(os.path.dirname(list(dep_freezer.venv_settings_files)[0].path)) == pathmaker(tmp_dir_fake_package.get('main_path'), 'fake_tools', 'venv_setup_settings')


def test_run_std_cmd(tmp_dir_fake_package):
    dep_freezer = DependencyFreezer(tmp_dir_fake_package.get('main_path'))
    assert dep_freezer.run_std_cmd(['ECHO', 'this_is_a_test']) == 'this_is_a_test\r\n'


def test_freeze(tmp_dir_fake_package, capsys):
    dep_freezer = DependencyFreezer(tmp_dir_fake_package.get('main_path'))
    dep_freezer.freeze(only_print=True)
    captured = capsys.readouterr()
    assert captured.out == """# required_dev.txt

	--> https://github.com/pyinstaller/pyinstaller/tarball/develop
	--> pep517==0.9.1
	--> memory-profiler==0.58.0
	--> matplotlib==3.3.3
	--> import-profiler==0.0.3
	--> objectgraph==1.0.1
	--> pipreqs==0.4.10
	--> pydeps==1.9.13
	--> --force-reinstall numpy==1.19.3
	--> pyqt5-tools==5.15.2.3
	--> PyQt5-stubs==5.14.2.2
	--> pyqtdeploy==3.1.0


--------------------


# required_misc.txt

	--> psutil==5.8.0
	--> Jinja2==2.11.2
	--> checksumdir==1.2.0
	--> click==7.1.2
	--> regex==2020.11.13
	--> parce==0.13.0
	--> fuzzywuzzy==0.18.0
	--> python-Levenshtein==0.12.0
	--> Pillow==8.0.0
	--> PyGithub==1.54
	--> discord.py==1.5.1
	--> discord_flags
	--> discord.py-stubs==1.5.1.2
	--> url-normalize==1.4.3
	--> async-property==0.2.1
	--> watchgod==0.6
	--> WeasyPrint==52.2
	--> pdfkit==0.6.1
	--> pytz==2020.4
	--> google-auth==1.24.0
	--> googletrans==4.0.0rc1
	--> google_api_python_client
	--> google_auth_oauthlib
	--> pyperclip==1.8.1
	--> pdfkit==0.6.1
	--> beautifulsoup4==4.9.3
	--> natsort==7.1.0
	--> jsonpickle==1.4.2
	--> marshmallow==3.10.0
	--> PyYAML==5.3.1


--------------------


# required_qt.txt

	--> PyQt5==5.15.2
	--> pyqt5-tools==5.15.2.3
	--> PyQt5-stubs==5.14.2.2
	--> PyOpenGL==3.1.5
	--> PyQt3D==5.15.2
	--> PyQtChart==5.15.2
	--> PyQtDataVisualization==5.15.2
	--> PyQtWebEngine==5.15.2
	--> QScintilla==2.11.6
	--> pyqtgraph==0.11.1
	--> parceqt==0.13.0


--------------------


# required_test.txt

	--> pytest==6.2.1
	--> pytest-qt==3.3.0
	--> pytest-cov==2.10.1


--------------------


"""
