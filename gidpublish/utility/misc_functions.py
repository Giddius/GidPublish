

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
import logging
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
from gidpublish.data.general_exclusions import GENERAL_FIXED_EXCLUDE_FOLDERS
from gidpublish.utility.enums import SearchReturn

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


def remove_unnecessary_lines(in_text: str, remove_filters: Iterable[Callable]):  # sourcery skip: list-comprehension
    _out = []
    for line in in_text.strip().splitlines():
        if line != '' and all(filter_func(line) for filter_func in remove_filters):
            _out.append(line)
    return '\n'.join(_out)


def find_file(in_dir, target_name: str, excluded_folder: Iterable[str] = None, target_type: str = 'file', loop_count=1):
    max_count = 5
    if loop_count > max_count:
        return

    for dirname, folderlist, filelist in os.walk(in_dir):
        if all(exclude_folder.casefold() not in dirname.casefold() for exclude_folder in excluded_folder):
            if target_type == 'file':
                for file in filelist:
                    if file.casefold() == target_name.casefold():
                        return pathmaker(dirname, file)
            elif target_type == 'folder':
                for folder in folderlist:
                    if folder.casefold() == target_name.casefold():
                        return pathmaker(dirname, folder)
    return find_file(pathmaker(in_dir, '../'), target_name, target_type, loop_count + 1)


def search_startswith(line: str, target_string: str, case_sensitive: bool = False):
    if case_sensitive is False:
        line = line.casefold()
        target_string = target_string.casefold()
    return line.startswith(target_string)


def search_endswith(line: str, target_string: str, case_sensitive: bool = False):
    if case_sensitive is False:
        line = line.casefold()
        target_string = target_string.casefold()
    return line.endswith(target_string)


def search_contains(line: str, target_string: str, case_sensitive: bool = False):
    if case_sensitive is False:
        line = line.casefold()
        target_string = target_string.casefold()
    return target_string in line


def find_in_content(start_dir, target_string: str, case_sensitive: bool = False, search_context: Callable = search_startswith, to_return: SearchReturn = SearchReturn.Both, in_loop=1):

    if in_loop > 5:
        return None
    for dirname, folderlist, filelist in os.walk(start_dir):
        if all(folder_exclude.casefold() not in dirname.casefold() for folder_exclude in GENERAL_FIXED_EXCLUDE_FOLDERS):
            for file in filelist:
                _path = pathmaker(dirname, file)
                try:
                    for line in readit(_path).splitlines():
                        if search_context(line, target_string, case_sensitive) is True:
                            if to_return is SearchReturn.Line:
                                return line
                            elif to_return is SearchReturn.File:
                                return _path
                            return (_path, line)
                except UnicodeDecodeError:
                    pass
    return find_in_content(pathmaker(start_dir, '../'), target_string, case_sensitive, search_context, to_return, in_loop + 1)

    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
