

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
from typing import Union, Iterable
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections.abc import Iterator
import psutil
# * Third Party Imports -->

# import requests
# import pyperclip
# import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from github import Github, GithubException
# from jinja2 import BaseLoader, Environment
# from natsort import natsorted
# from fuzzywuzzy import fuzz, process
from pipreqs import pipreqs
import toml

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


# * Local Imports -->
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)

from gidpublish.utility.named_tuples import DependencyItem, PipServerInfo, FreezeItem

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

VENV_SETTINGS_FILE_FORMAT = 'txt'

VENV_SETTINGS_MANDATORY_FILES = set(['post_setup_scripts.txt',
                                     'pre_setup_scripts.txt',
                                     'required_dev.txt',
                                     'required_from_github.txt',
                                     'required_misc.txt',
                                     'required_personal_packages.txt',
                                     'required_qt.txt',
                                     'required_test.txt'])

VENV_ACTIVATE_SCRIPT_NAME = 'activate.bat'
# endregion[Constants]


def _pip_list_clean(in_text: str):

    def remove_unnecessary_lines(in_text: str):
        _out = []
        for line in in_text.strip().splitlines():
            if not line.startswith('#') and not line.startswith('-') and line not in ['']:
                _out.append(line)
        return '\n'.join(_out)

    def create_package_items(in_text: str):
        normal = []
        from_git = []
        from_personal = []
        for line in in_text.splitlines():

            if '==' in line:
                name, version = line.strip().split('==')
                normal.append(FreezeItem(name, version))

            elif '@' in line:
                name, location = line.strip().split('@', 1)
                name = name.strip()
                location = location.strip()
                if location.startswith('git+https') or location.startswith('https:'):
                    from_git.append(FreezeItem(name, location, True))
                elif location.startswith('file'):
                    from_personal.append(FreezeItem(name, pathmaker(location), False, True))
                else:
                    raise TypeError(f'unknown value with name: "{name}" and location: "{location}"!')
        return normal, from_git, from_personal
    return(create_package_items(remove_unnecessary_lines(in_text)))


def _find_venv_activate_script(in_dir, loop_count=1, max_count=5):
    if loop_count > max_count:
        return
    for dirname, folderlist, filelist in os.walk(in_dir):
        for file in filelist:
            if file == VENV_ACTIVATE_SCRIPT_NAME:
                return pathmaker(dirname, file)
    return _find_venv_activate_script(pathmaker(in_dir, '../'), loop_count + 1, max_count=max_count)


def freeze_helper(in_dir, include_git=True, include_personal=True):
    activate_script = _find_venv_activate_script(in_dir)
    script = [activate_script, '&&', 'pip', 'freeze']
    cmd = subprocess.run(script, check=True, capture_output=True)
    cmd_output = cmd.stdout.decode('utf-8', errors='replace')
    normal_deps, git_deps, personal_deps = _pip_list_clean(cmd_output)
    out_items = normal_deps
    if include_git is True:
        out_items += git_deps
    if include_personal is True:
        out_items += personal_deps
    return out_items


def _find_matching_freeze_item(name, freeze_items):
    for item in freeze_items:
        if item.name.casefold() == name.casefold():
            return item
    return None


def _freeze_line(name, freeze_items, specifier):
    item = _find_matching_freeze_item(name, freeze_items)
    if item is None:
        return name
    return f"{item.name}{specifier}{item.data}"


def _get_venv_setup_files(in_folder):
    for file in os.scandir(in_folder):
        if os.path.isfile(file.path) and file.name.endswith(f".{VENV_SETTINGS_FILE_FORMAT}"):
            yield file.name, file.path, readit(file.path)


def _add_missing_files(existing_files, in_folder):
    for missing_file in VENV_SETTINGS_MANDATORY_FILES.difference(set(existing_files)):
        writeit(pathmaker(in_folder, missing_file), '')


def fix_venv_setup_settings(in_folder, specifier='>='):
    existing_files = []
    freeze_items = freeze_helper(in_folder, False, False)

    for file_name, file_path, file_content in _get_venv_setup_files(in_folder):
        _new_content_list = []

        for line in file_content.splitlines():
            if line != '' and not file_name.startswith('pre') and not file_name.startswith('post'):

                if "--force-reinstall" in line:
                    _new_content_list.append(line)

                else:
                    name = line.split('==')[0].split('>=')[0].split('>=')[0]
                    _new_content_list.append(_freeze_line(name, freeze_items, specifier).strip())

            elif file_name.startswith('pre') or file_name.startswith('post'):
                _new_content_list.append(line.strip())

        writeit(file_path, '\n'.join(_new_content_list))
        existing_files.append(file_name)
        _add_missing_files(existing_files, in_folder)


# region[Main_Exec]
if __name__ == '__main__':
    fix_venv_setup_settings(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidPublish\tools\venv_setup_settings", '==')

# endregion[Main_Exec]
