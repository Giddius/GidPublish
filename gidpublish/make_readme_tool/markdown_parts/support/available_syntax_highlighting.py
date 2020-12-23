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
from collections.abc import Iterable, Iterator


# * Third Party Imports -->

import requests
# import pyperclip
# import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from github import Github, GithubException
from jinja2 import BaseLoader, Environment, FileSystemLoader
# from natsort import natsorted
# from fuzzywuzzy import fuzz, process
from pipreqs import pipreqs
import toml
import yaml

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

from gidpublish.make_readme_tool.markdown_parts.basic.base_parts import BaseMarkdownStringFormatter
import gidpublish.make_readme_tool.markdown_parts.support.syntax_highlighting_data as syntax_highlighting_data_storage
from gidpublish.utility.named_tuples import SyntaxHighlightingLanguage
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
STORAGE_FOLDER = pathmaker(os.path.dirname(syntax_highlighting_data_storage.__file__))
GITHUB_SYNTAX_HIGHLIGHTING_YAML_URL = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"
STORAGE_FILE_BASE = pathmaker(STORAGE_FOLDER, "syntax_highlighting_languages")
STORAGE_FILE_YAML = STORAGE_FILE_BASE + '.yml'
STORAGE_FILE_JSON = STORAGE_FILE_BASE + '.json'
STORAGE_FILE_PICKLE = STORAGE_FILE_BASE + '.pkl'
# endregion[Constants]


def _to_named_tuple(content: dict):
    _out = []
    for key, value in content.items():
        _out.append(SyntaxHighlightingLanguage(name=key, aliases=value.get('aliases', []), group=value.get("group", 'misc'), extensions=value.get('extensions', []), type=value.get('type', 'general')))
    return _out


def _write_json_seperated(data: dict):
    for key, value in data.items():
        writejson(value, STORAGE_FILE_JSON.replace('languages', key), sort_keys=False, indent=4)


def _seperate_by_group(language_items):
    _out = {}
    for item in language_items:
        if item.group not in _out:
            _out[item.group] = []
        _out[item.group].append(item._asdict())

    _write_json_seperated(_out)


def _seperate_by_type(language_items):
    _out = {}
    for item in language_items:
        if item.type not in _out:
            _out[item.type] = []
        _out[item.type].append(item._asdict())

    _write_json_seperated(_out)


def _save_as_pickle(language_items):
    _out = {}
    for item in language_items:
        _out[item.name.casefold()] = item
    pickleit(_out, STORAGE_FILE_PICKLE)


def _yaml_to_json(clean_after=True, seperate=True, seperate_func=None, save_pickel=True):
    with open(STORAGE_FILE_YAML, 'rb') as f:
        content = yaml.safe_load(f)
    writejson(content, STORAGE_FILE_JSON, sort_keys=True, indent=4)
    language_items = _to_named_tuple(content)
    if save_pickel is True:
        _save_as_pickle(language_items)
    if seperate is True:
        if seperate_func is None:
            _seperate_by_group(language_items)
        else:
            seperate_func(language_items)
    if clean_after is True and os.path.isfile(STORAGE_FILE_YAML):
        os.remove(STORAGE_FILE_YAML)


def _download_syntax_highlighting_yaml(accept_404=True):

    result = requests.get(GITHUB_SYNTAX_HIGHLIGHTING_YAML_URL)
    if result.status_code == 404:
        if accept_404 is True:
            log.warning("received 404, ignored because 'accept_404' argument is set to 'True'")
            return False
        else:
            # TODO: custom error
            raise TypeError("received 404")
    for file in os.scandir(STORAGE_FOLDER):
        if file.is_file() and file.name != '__init__.py':
            os.remove(file.path)

    with open(STORAGE_FILE_YAML, 'wb') as f:
        f.write(result.content)
    _yaml_to_json()
    return True


class LoadType(Enum):
    Pickle = auto()
    Json = auto()


class LanguageHolder:
    Pickle = LoadType.Pickle
    Json = LoadType.Pickle
    last_updated_file = pathmaker(STORAGE_FOLDER, 'last_updated.pkl')
    update_cooldown = timedelta(days=1)

    def __init__(self, type_to_load: LoadType = None, refresh=True):
        self.last_updated = self.get_last_updated()
        self.type_to_load = self.Pickle if type_to_load is None else type_to_load
        if refresh is True and (self.last_updated is None or self.last_updated + self.update_cooldown < datetime.utcnow()):
            update = _download_syntax_highlighting_yaml()
            if update is True:
                self.last_updated = datetime.utcnow()
                pickleit(self.last_updated, self.last_updated_file)

    @property
    def languages(self):
        if self.type_to_load is LoadType.Pickle:
            return get_pickled(STORAGE_FILE_PICKLE)
        elif self.type_to_load is LoadType.Json:
            _out = {}
            for item in _to_named_tuple(loadjson(STORAGE_FILE_JSON)):
                _out[item.name.casefold()] = item
            return _out

    def get_last_updated(self):
        if os.path.isfile(self.last_updated_file) is False:
            return None
        return get_pickled(self.last_updated_file)

    def __getattr__(self, name):
        language_items = self.languages
        _language_item = language_items.get(name, None)
        if _language_item is None:
            for _name, item in language_items.items():
                if name in item.aliases:
                    _language_item = item
        if _language_item is None:
            raise AttributeError(f"Language '{name}' not found")
        return _language_item


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
