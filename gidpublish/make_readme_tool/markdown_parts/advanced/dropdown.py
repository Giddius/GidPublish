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
from textwrap import dedent

# * Third Party Imports -->

import requests
# import pyperclip
# import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from github import Github, GithubException
from jinja2 import BaseLoader, Environment, FileSystemLoader, PackageLoader
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


from gidpublish.make_readme_tool.markdown_parts.basic.simple_string_formatting import Bold, UnderScore, Cursive, LineCode
from gidpublish.make_readme_tool.markdown_parts.basic.block_formatting import CodeBlock, BlockQuote
from gidpublish.make_readme_tool.markdown_parts.support.available_syntax_highlighting import LanguageHolder
from gidpublish.utility.named_tuples import SyntaxHighlightingLanguage, DropdownItem
from gidpublish.template_handling.template_interface import TemplateHolderPackage


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]

log = glog.aux_logger(__name__)
log.info(glog.imported(__name__))

# endregion[Logging]

CodeBlock_Readme = partial(CodeBlock, indent=1)


def title_bold(title):
    return f"<b>{title}</b>"


class DropdownList:
    default_template_name = 'basic'
    content_item = DropdownItem

    def __init__(self, name, items=None):
        self.template_holder = TemplateHolderPackage(os.getenv('APP_NAME'), 'templates', 'gm_dropdown')
        self.name = name
        self.items = [] if items is None else items
        self.title_mod = None
        self.item_mods = {}
        self.general_indent = 0
        self.item_indent = 0
        self._active_template_name = None

    def __getattr__(self, name):
        return getattr(self.template_holder, name)

    @property
    def active_template_name(self):
        if self._active_template_name is None:
            return self.default_template_name
        return self._active_template_name

    @active_template_name.setter
    def active_template_name(self, name):
        if name not in self.available_templates:
            raise AttributeError(f"template with name '{name}' not found")
        self._active_template_name = name

    @active_template_name.deleter
    def active_template_name(self):
        self._active_template_name = None

    @property
    def active_template(self):
        return getattr(self, self.active_template_name)

    def add_item(self, name, **kwargs):
        self.items.append(self.content_item(name=str(name), **kwargs))

    def _wrap_items(self):
        _mod_items = []
        for item in self.items:
            for field in item._fields:
                _mod = self.item_mods.get(field + '_mod', None)
                if _mod:
                    item = item._replace(**{field: str(_mod(getattr(item, field)))})
            _mod_items.append(item)

        self.items = _mod_items

        if self.title_mod is not None:
            self.name = self.title_mod(self.name)

    def __str__(self):
        self._wrap_items()
        for xx in self.items:
            print(xx.description)
        return self.active_template.template.render(in_object=self)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
