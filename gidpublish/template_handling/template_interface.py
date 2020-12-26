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

# import requests
# import pyperclip
# import matplotlib.pyplot as plt
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from github import Github, GithubException
from jinja2 import BaseLoader, Environment, FileSystemLoader, PackageLoader, meta
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

from gidpublish.utility.named_tuples import TemplateMetaInfoItem, TemplateItem

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


class TemplateHolderBase:
    meta_item = TemplateMetaInfoItem
    template_item = TemplateItem

    def __init__(self, trim_blocks=True):
        self.trim_blocks = trim_blocks
        self.template_name_filter = self.filter_by_prefix
        self.template_prefix = None

    def _sanitize_to_attr_name(self, name: str):

        _replace_table = {
            ' ': '_',
            '-': '_'
        }
        modified_name = name.lower()
        if self.template_prefix is not None:
            modified_name = modified_name.replace(self.template_prefix, '')
            if modified_name.startswith('_'):
                modified_name = modified_name.lstrip('_')
        if '.' in modified_name:
            modified_name = modified_name.split('.')[0]
        if modified_name.isidentifier() is True:
            return modified_name
        for key, value in _replace_table.items():
            modified_name = modified_name.replace(key, value)
        if modified_name.isidentifier() is False:
            raise AttributeError(f'cannot sanitize template name "{name}" to valid attribute name, best result: "{modified_name}"')

        return modified_name

    @property
    def jinja_enviroment(self):
        return Environment(loader=self.loader(**self.loader_data), trim_blocks=self.trim_blocks)

    @property
    def available_templates(self):
        _template_names = self.jinja_enviroment.list_templates(filter_func=self.template_name_filter)
        return {self._sanitize_to_attr_name(template_name): template_name for template_name in _template_names}

    def get_source(self, full_template_name):
        env = self.jinja_enviroment
        return env.loader.get_source(env, full_template_name)

    def get_template_with_metainfo(self, name):
        template = self.jinja_enviroment.get_template(name)
        name = template.name
        file_name = template.filename
        source = self.get_source(name)
        variables = self.list_template_variables(source)
        return self.template_item(template=template, info=self.meta_item(name=name, file_name=file_name, source=source, vars=variables))

    def list_template_variables(self, template_source):
        parsed_content = self.jinja_enviroment.parse(template_source)
        return meta.find_undeclared_variables(parsed_content)

    def __getattr__(self, name):
        _template_name = self.available_templates.get(name, None)
        if _template_name is None:
            raise AttributeError(name)
        return self.get_template_with_metainfo(_template_name)

    def filter_by_prefix(self, template_name):
        return self.template_prefix is None or template_name.startswith(self.template_prefix)


class TemplateHolderPackage(TemplateHolderBase):
    def __init__(self, package_name, template_module_path, template_prefix=None, trim_blocks=True):
        super().__init__(trim_blocks=trim_blocks)
        self.loader = PackageLoader
        self.package_name = package_name
        self.template_module_path = self._check_fix_template_module_path(template_module_path)
        self.template_prefix = template_prefix

        self.loader_data = {"package_name": self.package_name, "package_path": self.template_module_path}

    def _check_fix_template_module_path(self, path):
        if not path.startswith(self.package_name):
            return path
        path_parts = path.split('/')
        path_parts.pop(0)
        return '/'.join(path_parts)


# region[Main_Exec]


if __name__ == '__main__':
    pass


# endregion[Main_Exec]
