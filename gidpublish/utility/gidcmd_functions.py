

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
from typing import Union, Callable
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import shutil
import shelve
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
import psutil

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

from gidpublish.utility.gidtools_functions import pathmaker
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

GIT_EXE = shutil.which('git.exe')

# endregion[Constants]


class CaptureMode(Enum):
    NONE = auto()
    STDOUT = auto()
    STDERR = auto()
    BOTH = auto()


CAPTURE_MAP = {CaptureMode.STDOUT: {'capture_output': True},
               CaptureMode.STDERR: {'capture_output': True},
               CaptureMode.BOTH: {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT},
               CaptureMode.NONE: {'capture_output': False}}


def _find_drives(sort: bool = True, largest_first: bool = False):
    drps = psutil.disk_partitions()
    drives = [dp.device for dp in drps if dp.fstype == 'NTFS']
    _out = [(drive, psutil.disk_usage(drive).used) for drive in drives]
    if sort is True:
        _out = sorted(_out, key=lambda x: x[1], reverse=largest_first)
    return [drive_name for drive_name, size in _out]


def _wide_search_executable(executable_name: str):
    executable_name = executable_name.replace(os.pathsep, '/').casefold()
    bare_executable_name = os.path.splitext(executable_name)[0]
    print(executable_name)
    _out = shutil.which(executable_name)
    print(_out)
    if _out is None:
        for drive in _find_drives():
            for dirname, folderlist, filelist in os.walk(drive):
                for file in filelist:
                    if '/' in executable_name:
                        if executable_name in os.path.join(dirname, file).replace(os.pathsep, '/').casefold() or bare_executable_name in os.path.join(dirname, file).replace(os.pathsep, '/').casefold():
                            return os.path.join(dirname, file).replace(os.pathsep, '/')
                    else:
                        if file.casefold() in [executable_name, bare_executable_name]:
                            return os.path.join(dirname, file).replace(os.pathsep, '/')
    return _out


def path_cmd(executable: str, command: list, output_handler: Callable = None, check: bool = True, capture_mode: CaptureMode = CaptureMode.BOTH, ** subprocess_run_kwargs):
    executable_name = executable
    executable = shutil.which(executable)
    if executable is None:
        raise FileNotFoundError(f'could not locate executable "{executable_name}" on PATH')
    full_command = [executable] + command
    capture_settings = CAPTURE_MAP.get(capture_mode)
    cmd = subprocess.run(full_command, check=check, **capture_settings, ** subprocess_run_kwargs)
    if capture_mode in [CaptureMode.STDOUT, CaptureMode.BOTH]:
        cmd_output = cmd.stdout.decode('utf-8', errors='replace')
    else:
        cmd_output = cmd.stderr.decode('utf-8', errors='replace')
    if output_handler is not None:
        output_handler(cmd_output)
    else:
        return cmd_output


def find_executable(executable: str):
    return _wide_search_executable(executable_name=executable)


def base_folder_from_git():
    cmd = subprocess.run([GIT_EXE, "rev-parse", "--show-toplevel"], capture_output=True, text=True, shell=True, check=True)
    base_folder = pathmaker(cmd.stdout.rstrip('\n'))
    if os.path.isdir(base_folder) is False:
        raise FileNotFoundError('Unable to locate main dir of project')
    return base_folder


# region[Main_Exec]
if __name__ == '__main__':
    pass


# endregion[Main_Exec]
