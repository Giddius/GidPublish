

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
from enum import Enum, Flag, auto, unique
from time import sleep
from pprint import pprint, pformat
from typing import Union, Iterable, Union, Optional, List, Callable, Set, Tuple, Dict, Iterator, TYPE_CHECKING, Any
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections.abc import Iterator
from itertools import chain
import psutil
from packaging import version
from xml import etree as et
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
from lxml import etree, objectify
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
from pathlib import PurePath, Path

# * Local Imports -->
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)

from gidpublish.data.general_exclusions import GENERAL_FIXED_EXCLUDE_FOLDERS
from gidpublish.utility.enums import SearchReturn, VersionPart, FileType
from gidpublish.utility.misc_functions import find_in_content, search_endswith, search_contains, search_startswith
from gidpublish.utility.gidtools_functions import work_in
from string import ascii_lowercase, ascii_uppercase, ascii_letters
from gidpublish.utility.gidcmd_functions import base_folder_from_git
from abc import ABC, ABCMeta, abstractmethod
from glob import iglob
from gidpublish.utility.misc_functions import debug_timing_print
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

# endregion[Constants]


class VersionItem:
    version_regex = re.compile(r"(?P<major>\d+)(?P<separator>.+)(?P<minor>\d+)(?P=separator)(?P<patch>\d+)")

    def __init__(self, major: int, minor: int, patch: int, separator: str):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.separator = separator

    @classmethod
    def from_string(cls, version_string: str):
        version_match = cls.version_regex.search(version_string.strip())

        if version_match:
            match_dict = version_match.groupdict()
            for key, value in match_dict.items():
                match_dict[key] = int(value) if value.isdigit() else value
            return cls(**match_dict)
        else:
            raise version.InvalidVersion(version_string)

    @property
    def parts(self):
        return [self.major, self.minor, self.patch]

    def increment(self, inc_part: VersionPart):
        for part in VersionPart:
            if part is inc_part:
                self.set(part, getattr(self, part.attr_name) + 1)
            elif part < inc_part:
                self.set(part, 0)

    def set(self, part: VersionPart, value):
        if not isinstance(value, int):
            value = int(value)
        setattr(self, part.attr_name, value)

    def __str__(self) -> str:
        return self.separator.join(map(str, self.parts))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(major={self.major}, minor={self.minor}, patch={self.patch}, separator={self.separator})"


class AbstractVersionHandler(ABC):
    auto_write = True

    @classmethod
    @property
    @abstractmethod
    def version_line_identifier(cls) -> str:
        ...

    @classmethod
    @property
    @abstractmethod
    def version_replace_regex(cls) -> Tuple[re.Pattern, str]:
        ...

    @classmethod
    @property
    @abstractmethod
    def quote_version(cls) -> bool:
        ...

    def __init__(self, base_folder: Union[str, os.PathLike], **kwargs):
        self.base_folder = base_folder
        self.version_file = self._find_version_file()
        self.version_line = self._find_version_line()
        self.version = self._extract_version()

    @abstractmethod
    def _find_version_file(self):
        ...

    @abstractmethod
    def _find_version_line(self):
        ...

    @abstractmethod
    def _extract_version(self):
        ...

    def refresh(self):
        self.version_file = self._find_version_file()
        self.version_line = self._find_version_line()
        self.version = self._extract_version()

    def increment_version(self, increment_part: VersionPart):
        self.version.increment(increment_part)
        if self.auto_write is True:
            self.write()

    def write(self):
        version_string = f'"{self.version}"' if self.quote_version is True else str(self.version)
        new_content = self.version_replace_regex[0].sub(self.version_replace_regex[1].format(version_string), readit(self.version_file))
        writeit(self.version_file, new_content)

    def set(self, part: VersionPart, value):
        self.version.set(part, value)
        if self.auto_write is True:
            self.write()


class PythonFlitVersionHandler(AbstractVersionHandler):
    version_line_identifier = '__version__'
    quote_version = True
    version_replace_regex = (re.compile(rf"(?P<identifier>{version_line_identifier})(?P<operator>\s?.\s?)(?P<version>.*)"), r"\g<identifier>\g<operator>{}")
    default_venv_name = '.venv'
    version_class = VersionItem

    def __init__(self, base_folder: Union[str, os.PathLike], **kwargs):
        self.venv_name = self.default_venv_name if kwargs.get('venv_name') is None else kwargs.get('venv_name')
        super().__init__(base_folder)

    def _find_version_file(self):
        with work_in(self.base_folder):
            for path in iglob('**/__init__.py', recursive=True):
                path = os.path.abspath(path)
                if self.venv_name not in path.casefold():
                    content = readit(path)
                    if self.version_line_identifier in content:
                        return path

    def _find_version_line(self):
        with open(self.version_file, 'r') as f:
            for line in f:
                if self.version_line_identifier in line:
                    return line.strip()

    def _extract_version(self):
        cleaned_version_line = self.version_line.removeprefix(self.version_line_identifier).replace('=', '').strip(r"\s\'\"\n")
        return self.version_class.from_string(cleaned_version_line)


class VersionManager:
    MAJOR = VersionPart.MAJOR
    MINOR = VersionPart.MINOR
    PATCH = VersionPart.PATCH

    version_handler = PythonFlitVersionHandler

    def __init__(self, base_folder: Union[str, os.PathLike] = None):
        self.base_folder = base_folder if base_folder is not None else base_folder_from_git()
        self.version_handler = self.version_handler(self.base_folder)

    def __getattr__(self, name):
        if hasattr(self.version_handler, name):
            return getattr(self.version_handler, name)
        raise AttributeError(name)

    @classmethod
    def set_auto_write(cls, value: bool):
        cls.version_handler.auto_write = value


        # region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
