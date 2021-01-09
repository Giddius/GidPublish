"""
[summary]

[extended_summary]
"""

# region [Imports]

# * Standard Library Imports ------------------------------------------------------------------------------------------------------------------------------------>

import gc
import os
import re
import sys
import json
import lzma
import time
import queue
import base64
import pickle
import random
import shelve
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import unicodedata

from io import BytesIO
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import Union, Callable, Iterable, Dict, Tuple
from inspect import stack, getdoc, getmodule, getsource, getmembers, getmodulename, getsourcefile, getfullargspec, getsourcelines
from zipfile import ZipFile
from datetime import tzinfo, datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering
from importlib import import_module, invalidate_caches
from contextlib import contextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from glob import glob

# * Third Party Imports ----------------------------------------------------------------------------------------------------------------------------------------->

# import discord

# import requests

# import pyperclip

# import matplotlib.pyplot as plt

# from bs4 import BeautifulSoup

# from dotenv import load_dotenv

# from discord import Embed, File

# from discord.ext import commands, tasks

# from github import Github, GithubException

# from jinja2 import BaseLoader, Environment

# from natsort import natsorted

# from fuzzywuzzy import fuzz, process


# * PyQt5 Imports ----------------------------------------------------------------------------------------------------------------------------------------------->

# from PyQt5.QtGui import QFont, QIcon, QBrush, QColor, QCursor, QPixmap, QStandardItem, QRegExpValidator

# from PyQt5.QtCore import (Qt, QRect, QSize, QObject, QRegExp, QThread, QMetaObject, QCoreApplication,
#                           QFileSystemWatcher, QPropertyAnimation, QAbstractTableModel, pyqtSlot, pyqtSignal)

# from PyQt5.QtWidgets import (QMenu, QFrame, QLabel, QAction, QDialog, QLayout, QWidget, QWizard, QMenuBar, QSpinBox, QCheckBox, QComboBox, QGroupBox, QLineEdit,
#                              QListView, QCompleter, QStatusBar, QTableView, QTabWidget, QDockWidget, QFileDialog, QFormLayout, QGridLayout, QHBoxLayout,
#                              QHeaderView, QListWidget, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout, QWizardPage,
#                              QApplication, QButtonGroup, QRadioButton, QFontComboBox, QStackedWidget, QListWidgetItem, QSystemTrayIcon, QTreeWidgetItem,
#                              QDialogButtonBox, QAbstractItemView, QCommandLinkButton, QAbstractScrollArea, QGraphicsOpacityEffect, QTreeWidgetItemIterator)


# * Gid Imports ------------------------------------------------------------------------------------------------------------------------------------------------->

import gidlogger as glog


# * Local Imports ----------------------------------------------------------------------------------------------------------------------------------------------->
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file, remove_extension, get_ext)

from gidpublish.utility.gidcmd_functions import (find_executable, path_cmd, CaptureMode)
from gidpublish.abstracts.abstract_workjob_interface import AbstractBaseWorkjob
from gidpublish.utility.exceptions import UnsetExecutableError
from gidpublish.utility.named_tuples import CliMappingItem
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

THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
SHELVE_FILE = pathmaker(THIS_FILE_DIR, 'found_executable_shelve')

# endregion[Constants]


def _save_executable_path(path):
    shelve_dict = shelve.open(SHELVE_FILE)
    name_original = os.path.basename(path).casefold()
    name_stripped_ext = remove_extension(name_original).casefold()
    path = pathmaker(path)
    shelve_dict[name_original] = path
    shelve_dict[name_stripped_ext] = path
    shelve_dict.close()


def _get_shelved_executable_path(name):
    name = name.casefold()
    shelve_dict = shelve.open(SHELVE_FILE)
    if name in shelve_dict:
        _out = shelve_dict[name] if os.path.isfile(shelve_dict[name]) is True else None
    else:
        _out = None
    shelve_dict.close()
    return _out


def determine_exectuable_path(executable_name):
    executable_path = shutil.which(executable_name)
    if executable_path is None:
        executable_path = _get_shelved_executable_path(executable_name)
    if executable_path is None:
        executable_path = find_executable(executable_name)
        if executable_path is not None:
            _save_executable_path(executable_path)
    if executable_path is None:
        raise FileNotFoundError(f"could not finde executable '{executable_name}'")
    return pathmaker(executable_path)


class ApplyMode(Enum):
    ALL = auto()
    SINGLE_FILES = auto()
    GLOB = auto()


class CliRunner(AbstractBaseWorkjob):
    config_section = 'cli_runner'
    ALL = ApplyMode.ALL
    GLOB = ApplyMode.GLOB
    SINGLE_FILES = ApplyMode.SINGLE_FILES

    def __init__(self, executables: list[Tuple[str, Iterable]], target_dir, apply_map: Dict[str, CliMappingItem] = None):
        self.target_dir = pathmaker(target_dir)
        self.raw_executables = executables
        self.ensured_executables = None
        self.full_commands = None
        self.exclusions = []
        self.apply_map = {} if apply_map is None else apply_map
        self.resolved_apply_map = None
        self.all_files = self._get_all_files()
        self.is_venv = 'venv' in sys.executable.casefold()
        if self.is_venv:
            os.environ['PATH'] += ';' + pathmaker(sys.executable, '../')

    def add_to_apply_map(self, executable: str, mapping: CliMappingItem):
        mod_executable = remove_extension(executable).casefold()
        if mod_executable not in self.apply_map:
            raise UnsetExecutableError(executable)
        self.apply_map[mod_executable] = mapping

    def _ensure_executable_map(self):
        _mod_map = {}
        for key, value in self.apply_map.items():
            key = remove_extension(key).casefold()
            _mod_map[key] = value
        self.apply_map = _mod_map

        for executable, command in self.raw_executables:
            executable = remove_extension(executable).casefold()
            if executable not in self.apply_map:
                self.apply_map[executable] = None

    def _ensure_executable_paths(self):
        self.executable_paths = []
        self.ensured_executables = {}
        for executable, command in self.raw_executables:
            executable_key = remove_extension(executable).casefold()
            if os.path.isfile(executable) is True:
                self.executable_paths.append(executable)
                self.ensured_executables[executable_key] = [executable] + command
            else:
                executable_path = determine_exectuable_path(executable)
                self.executable_paths.append(executable_path)
                self.ensured_executables[executable_key] = [executable_path] + command

    def _get_all_files(self):
        _out = []
        for dirname, folderlist, filelist in os.walk(self.target_dir):
            for file in filelist:
                _out.append(pathmaker(dirname, file))
        return _out

    def _convert_mapping(self):
        self.resolved_apply_map = {}
        for executable, mapping in self.apply_map.items():
            if mapping.typus is ApplyMode.ALL:
                self.resolved_apply_map[executable] = self.all_files
            elif mapping.typus is ApplyMode.SINGLE_FILES:
                self.resolved_apply_map[executable] = list(map(pathmaker, mapping.files))
            elif mapping.typus is ApplyMode.GLOB:
                self.resolved_apply_map[executable] = []
                for pattern in mapping.pattern:
                    self.resolved_apply_map[executable].append(glob(self.target_dir + '/' + pattern, recursive=True))

    def execute_executable(self, ensured_executable, target):
        os.environ['TARGETFILE'] = remove_extension(target)
        os.environ['FULLTARGETFILE'] = target
        if self.is_venv:
            ensured_executable = ['call', pathmaker(sys.executable, '../', 'activate.bat'), '&&', 'call'] + ensured_executable
        cmd = subprocess.run(ensured_executable, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=os.environ)
        _output = cmd.stdout.decode('utf-8', errors='replace')
        print(_output)
        log.info(_output)

    def execute_all(self):
        self._ensure_executable_paths()
        self._ensure_executable_map()
        self._convert_mapping()
        for key, ensured_executable in self.ensured_executables.items():
            for file in self.resolved_apply_map.get(key):
                self.execute_executable(ensured_executable, file)

    @classmethod
    def configure(cls, config):
        pass

    def work(self):
        pass

    def add_exclusion(self, exclusion_item):
        pass

    @classmethod
    def config_entries(cls):
        pass

    @classmethod
    def extra_dependencies(cls):
        pass

# region[Main_Exec]


if __name__ == '__main__':
    x = CliRunner([('pyclean', ['-v', r'%FULLTARGETFILE%']), ('pipreqs', [r'%FULLTARGETFILE%'])], pathmaker('./'),
                  {'pyclean': CliMappingItem(ApplyMode.SINGLE_FILES, files=['../../']), 'pipreqs': CliMappingItem(CliRunner.SINGLE_FILES, files=[pathmaker('../')])})
    x.execute_all()

# endregion[Main_Exec]
