

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
from itertools import chain
import psutil
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


# * Local Imports -->
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)

from gidpublish.data.general_exclusions import GENERAL_FIXED_EXCLUDE_FOLDERS
from gidpublish.utility.enums import SearchReturn, VersionParts, FileType
from gidpublish.utility.misc_functions import find_in_content, search_endswith, search_contains, search_startswith
from string import ascii_lowercase, ascii_uppercase, ascii_letters
from gidpublish.utility.named_tuples import VersionItem, VersionHandleItem

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


class VersionManager:
    VERSION_MAJOR = VersionParts.Major
    VERSION_MINOR = VersionParts.Minor
    VERSION_PATCH = VersionParts.Patch

    def __init__(self, in_file_folder, identifier: str, is_next_line: bool = False, version_max: int = None):
        self.handle_table = {FileType.Xml: VersionHandleItem(self._get_version_xml, self._write_version_xml),
                             FileType.Text: VersionHandleItem(self._get_version_text, self._write_version_text),
                             FileType.Python: VersionHandleItem(self._get_version_text, self._write_version_text),
                             FileType.Markdown: VersionHandleItem(self._get_version_text, self._write_version_text)}
        self.xml_settings = {'identifier_attribute': 'ID', 'version_tag': 'Original'}
        self.file_or_folder = in_file_folder
        self.file_type = FileType(None)
        self.identifier = identifier
        self.is_next_line = is_next_line
        self.version_max = version_max
        self.version_seperator = '.'
        self.version_line = None
        self.original_version = None
        self.version = None
        self.downstream_version_holder = []
        self._check_in_file_folder()

    @property
    def version_regex(self):
        return re.compile(r"(?P<major>\d+)" + "\\" + self.version_seperator + r"(?P<minor>\d+)" + "\\" + self.version_seperator + r"?(?P<patch>[\d+])?")

    @lru_cache()
    def xml_parsed_tree(self):
        if self.file_type is not FileType.Xml:
            raise TypeError
        tree = etree.parse(self.file_or_folder, parser=etree.XMLParser())
        root = tree.getroot()
        return tree, root

    @lru_cache()
    def text_lines(self):
        if self.file_type not in [FileType.Text, FileType.Python, FileType.Markdown]:
            raise TypeError
        return readit(self.file_or_folder).splitlines()

    def _check_in_file_folder(self):
        if os.path.isdir(self.file_or_folder):
            self.file_or_folder = find_in_content(self.file_or_folder, self.identifier, False, search_contains, SearchReturn.File)
            if self.file_or_folder is None:
                raise FileNotFoundError
            self.file_type = FileType(os.path.splitext(self.file_or_folder)[1])
        elif os.path.isfile(self.file_or_folder):
            self.file_type = FileType(os.path.splitext(self.file_or_folder)[1])
        else:
            raise TypeError

    def increment(self, increment_type: VersionParts):
        if self.version is None:
            self.get_version()
        max_value = self.version_max if self.version_max is not None else 999999999
        if self.version.patch is None and increment_type is self.VERSION_PATCH:
            new_version = self.version._replace(patch=1)
        else:
            new_version = self.version._replace(**{increment_type.name.casefold(): self.version[increment_type.value] + 1})
            if increment_type is not self.VERSION_MAJOR and new_version[increment_type.value] >= max_value:
                new_version = new_version._replace(**{increment_type.name.casefold(): 0})
                next_part = VersionParts(increment_type.value - 1)
                new_version = new_version._replace(**{next_part.name.casefold(): new_version[next_part.value] + 1})
                if next_part is not self.VERSION_MAJOR and new_version[next_part.value] >= max_value:
                    next_next_part = VersionParts(next_part.value - 1)
                    new_version = new_version._replace(**{next_part.name.casefold(): 0, next_next_part.name.casefold(): new_version[next_next_part.value] + 1})
        self.version = new_version
        self.apply_downstream()

    def apply_downstream(self):
        for downstream_holder in self.downstream_version_holder:
            downstream_holder.version = self.version
            downstream_holder.original_version = self.original_version

    def write_downstream(self):
        for downstream_holder in self.downstream_version_holder:
            downstream_holder.write_version()

    def get_version(self):
        string_result = self.handle_table.get(self.file_type).get_version()
        regex_result = self.version_regex.search(string_result)
        if regex_result:
            version_parts = VersionItem(**{key: int(value) for key, value in regex_result.groupdict().items() if value is not None}, seperator=self.version_seperator)
            self.version_line = string_result
            self.original_version = version_parts
            self.version = VersionItem(**version_parts._asdict())
            self.apply_downstream()
        return self.original_version

    def _get_version_text(self):
        lines = self.text_lines()
        for index, line in enumerate(lines):
            if self.identifier.casefold() in line.casefold():
                if self.is_next_line is True:
                    line = lines[index + 1]
                return line

    def _get_version_xml(self):
        tree, root = self.xml_parsed_tree()
        for elem in root.getiterator():
            if elem.attrib.get(self.xml_settings.get('identifier_attribute')) == self.identifier:
                for child in elem.getchildren():
                    if child.tag == self.xml_settings.get('version_tag'):
                        return str(child.text)

    def _write_version_xml(self):
        tree, root = self.xml_parsed_tree()
        for elem in root.getiterator():
            if elem.attrib.get(self.xml_settings.get('identifier_attribute')) == self.identifier:
                for child in elem.getchildren():
                    if child.tag == self.xml_settings.get('version_tag'):
                        child.text = self.version.version_string
        tree_str = etree.tostring(tree.getroot(), encoding='utf-8', pretty_print=True, xml_declaration=True)
        writebin(self.file_or_folder, tree_str)

    def _write_version_text(self):
        _new_lines = []
        lines = self.text_lines()
        for index, line in enumerate(lines):
            if self.identifier.casefold() in line.casefold():
                if self.is_next_line is True:
                    line = lines[index + 1]
                line = self.version_regex.sub(self.version.version_string, line)
            _new_lines.append(line)
        writeit(self.file_or_folder, '\n'.join(_new_lines))

    def write_version(self, downstream=True):
        self.handle_table.get(self.file_type).write_version()
        if downstream is True:
            self.write_downstream()


        # region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
