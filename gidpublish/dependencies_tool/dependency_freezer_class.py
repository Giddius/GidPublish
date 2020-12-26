

# region [Imports]

# * Standard Library Imports -->

import asyncio
import gc
import logging
import os
import re
import sys
import json
import lzma
import time
import queue

import platform
import subprocess
from enum import Enum, Flag, auto
from time import sleep
from pprint import pprint, pformat
from typing import Union, Callable, Iterable
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from textwrap import indent

# * Third Party Imports -->
from itertools import chain
# import requests
# import pyperclip
# import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
from dotenv import load_dotenv
# from github import Github, GithubException
# from jinja2 import BaseLoader, Environment
# from natsort import natsorted
# from fuzzywuzzy import fuzz, process


# * PyQt5 Imports -->

# from PyQt5.QtGui import QFont, QIcon, QBrush, QColor, QCursor, QPixmap, QStandardItem, QRegExpValidator
# from PyQt5.QtCore import (Qt, QRect, QSize, QObject, QRegExp, QThread, QMetaObject, QCoreApplication,
#                           QFileSystemWatcher, QPropertyAnimation, QAbstractTableModel, pyqtSlot, pyqtSignal)
# from PyQt5.QtWidgets import (QMenu, QFrame, QLabel, QDialog, QLayout, QWidget, QWizard, QMenuBar, QSpinBox, QCheckBox, QComboBox,
#                              QGroupBox, QLineEdit, QListView, QCompleter, QStatusBar, QTableView, QTabWidget, QDockWidget, QFileDialog,
#                              QFormLayout, QGridLayout, QHBoxLayout, QHeaderView, QListWidget, QMainWindow, QMessageBox, QPushButton,
#                              QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout, QWizardPage, QApplication, QButtonGroup, QRadioButton,
#                              QFontComboBox, QStackedWidget, QListWidgetItem, QTreeWidgetItem, QDialogButtonBox, QAbstractItemView,
#                              QCommandLinkButton, QAbstractScrollArea, QGraphicsOpacityEffect, QTreeWidgetItemIterator, QAction, QSystemTrayIcon)


# * Gid Imports -->

import gidlogger as glog
from gidtools.gidfiles import (QuickFile, readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                               dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)


# * Local Imports -->
from gidpublish.abstracts.abstract_workjob_interface import AbstractBaseWorkjob
from gidpublish.utility.named_tuples import FreezeItem, VenvSettingsFileItem
from gidpublish.utility.enums import CmdReturn, VenvSettingFileTypus
from gidpublish.utility.exceptions import UnknownFreezeValue
from gidpublish.utility.misc_functions import remove_unnecessary_lines
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]

log = glog.aux_logger(__name__)
log.info(glog.imported(__name__))

# endregion[Logging]

# region [Constants]


# endregion[Constants]


def _get_settings_file_typus(in_file_name):
    if in_file_name in ['post_setup_scripts.txt', 'pre_setup_scripts.txt']:
        return VenvSettingFileTypus.SetupScript
    elif '_github' in in_file_name:
        return VenvSettingFileTypus.FromGithub
    elif '_personal' in in_file_name:
        return VenvSettingFileTypus.Personal
    elif '_dev' in in_file_name:
        return VenvSettingFileTypus.Dev
    else:
        return VenvSettingFileTypus.Normal


class DependencyFreezer(AbstractBaseWorkjob):
    config_section = 'dependency_freezer'
    venv_activate_script_name = 'activate.bat'
    venv_settings_file_format = '.txt'
    venv_settings_folder_name = 'venv_setup_settings'
    venv_settings_mandatory_files = set(['post_setup_scripts.txt',
                                         'pre_setup_scripts.txt',
                                         'required_dev.txt',
                                         'required_from_github.txt',
                                         'required_misc.txt',
                                         'required_personal_packages.txt',
                                         'required_qt.txt',
                                         'required_test.txt'])
    default_version_specifier = '=='

    def __init__(self, target_dir):

        self.target_dir = None
        self.set_target_dir(target_dir)
        self.project_devmeta_env_file = self._find_file(self.target_dir, '_project_devmeta.env')
        load_dotenv(self.project_devmeta_env_file, override=True)
        self.special_paths = {'venv_activate_script': self._find_file(self.target_dir, self.venv_activate_script_name, 'file'),
                              'venv_settings_folder': self._find_file(self.target_dir, self.venv_settings_folder_name, 'folder'),
                              'workspace_folder': pathmaker(os.getenv('WORKSPACEDIR')),
                              'toplevel_module': pathmaker(os.getenv('TOPLEVELMODULE')),
                              'main_script_file': pathmaker(os.getenv('MAIN_SCRIPT_FILE'))}

        self._check_special_paths()
        self.version_specifier = self.default_version_specifier
        self.frozen_package_data = None

    @property
    def venv_settings_files(self):
        for settings_file in os.scandir(self.special_paths.get('venv_settings_folder')):
            if settings_file.is_file() and settings_file.name.endswith(self.venv_settings_file_format):
                name = settings_file.name.casefold()
                path = pathmaker(settings_file.path)
                typus = _get_settings_file_typus(name)
                content = readit(settings_file.path)
                yield VenvSettingsFileItem(name=name, path=path, content=content, typus=typus)

    @property
    def _command_venv_activation(self):
        return [self.special_paths.get('venv_activate_script'), '&&']

    def _find_matching_freeze_item(self, in_name: str):

        for freeze_item in chain(*[value for key, value in self.frozen_package_data.items()]):
            if freeze_item.name.casefold() == in_name.casefold():
                return freeze_item

    def _freeze_line(self, name):
        item = self._find_matching_freeze_item(name)
        if item is None:
            return name
        return f"{item.name}{self.version_specifier}{item.data}"

    def run_std_cmd(self, in_command: list, activate_venv: bool = True, capture: CmdReturn = CmdReturn.Stdout, output_cleaner: Callable = None):
        # sourcery skip: simplify-boolean-comparison

        command = self._command_venv_activation + in_command if activate_venv is True else in_command

        cmd = subprocess.run(command, check=True, capture_output=True, shell=False)
        cmd_output = getattr(cmd, capture.value, b'').decode('utf-8', errors='replace')

        if output_cleaner is not None:
            cmd_output = output_cleaner(in_text=cmd_output)
        return cmd_output

    def _create_package_data(self, in_text: str):
        self.frozen_package_data = {'normal': [], 'git': [], 'personal': []}
        for line in in_text.splitlines():
            line = line.strip()
            if '==' in line:
                name, version = line.split('==')
                self.frozen_package_data['normal'].append(FreezeItem(name, version))
            elif '@' in line:
                name, location = line.split(' @ ', 1)
                if location.startswith('git+https') or location.startswith('https:'):
                    self.frozen_package_data['git'].append(FreezeItem(name, location, is_github=True))
                elif location.startswith('file:///'):
                    self.frozen_package_data['personal'].append(FreezeItem(name, pathmaker(location.replace('file:///', '')), is_personal=True))
            else:
                raise UnknownFreezeValue(line)

    def freeze(self, include_github=False, include_personal=False, include_dev=True, only_print=False):

        execution_command = ['pip', 'freeze']
        freeze_text = self.run_std_cmd(execution_command, output_cleaner=partial(remove_unnecessary_lines, remove_filters=[lambda x: not x.startswith('#') and not x.startswith('-')]))
        self._create_package_data(freeze_text)
        exclusion_types = [VenvSettingFileTypus.SetupScript] + [item[0] for item in
                                                                [(VenvSettingFileTypus.FromGithub, include_github),
                                                                 (VenvSettingFileTypus.Personal, include_personal),
                                                                 (VenvSettingFileTypus.Dev, include_dev)]
                                                                if item[1] is False]
        for settings_file_item in self.venv_settings_files:
            _new_content = []
            if settings_file_item.typus in exclusion_types:
                continue
            for line in settings_file_item.content.splitlines():
                if line != '':
                    if "--force-reinstall" in line:
                        _new_content.append(line)
                    else:
                        name = line.split('==')[0].split('>=')[0].split('>=')[0]
                        _new_content.append(self._freeze_line(name).strip())
            _new_content = '\n'.join(_new_content).strip()
            if only_print is True:
                print(f'# {settings_file_item.name}\n')
                print(indent(_new_content, '\t--> '))
                print('\n\n--------------------\n\n')
            else:
                writeit(settings_file_item.path, _new_content)

    def _check_special_paths(self):
        if self.project_devmeta_env_file is None:
            raise FileNotFoundError("was not able to find 'project_devmeta_env_file'")
        for key, value in self.special_paths.items():
            if value is None:
                raise FileNotFoundError(f"was not able to find '{key}'")

    def _find_file(self, in_dir, target_name, target_type='file', loop_count=1):
        max_count = 5
        if loop_count > max_count:
            return

        for dirname, folderlist, filelist in os.walk(in_dir):
            if 'tests' not in dirname:
                if target_type == 'file':
                    for file in filelist:
                        if file.casefold() == target_name.casefold():
                            return pathmaker(dirname, file)
                elif target_type == 'folder':
                    for folder in folderlist:
                        if folder.casefold() == target_name.casefold():
                            return pathmaker(dirname, folder)
        return self._find_file(pathmaker(in_dir, '../'), target_name, target_type, loop_count + 1)

    def ensure_mandatory_files(self):
        for mandatory_file in list(self.venv_settings_mandatory_files):
            if mandatory_file not in map(lambda x: x.name, self.venv_settings_files):
                path = pathmaker(self.special_paths.get('venv_settings_folder'), mandatory_file)
                if os.path.isfile(path) is False:
                    writeit(path, '')

    def set_target_dir(self, target_dir):
        target_dir = pathmaker(target_dir)
        if os.path.exists(target_dir) is False:
            raise FileNotFoundError(f'argument "target_dir"("{target_dir}"), does not point to an existing directory')
        self.target_dir = target_dir

    @ classmethod
    def configure(cls, config):
        pass

    def work(self):
        pass

    def add_exclusion(self, exclusion_item):
        pass


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
