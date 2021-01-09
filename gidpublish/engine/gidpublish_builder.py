

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
from typing import Union, Iterable, Tuple
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections.abc import Iterator
from importlib.machinery import SourceFileLoader
from importlib import import_module, reload as module_reload, invalidate_caches
from importlib.util import spec_from_file_location, find_spec, module_from_spec
import shutil
import inspect
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
import click

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
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson, get_parent_dir,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file, get_ext, remove_extension)
from gidtools.gidimport.special_kind_of_imports import import_from_path
from gidpublish.utility.named_tuples import DependencyItem, PipServerInfo
from gidpublish.abstracts.abstract_workjob_interface import AbstractBaseWorkjob
from gidpublish.utility.misc_functions import remove_unnecessary_lines, find_file
from gidpublish.data.general_exclusions import GENERAL_FIXED_EXCLUDE_FOLDERS
from gidpublish.engine.stored_tool_item import StoredTool
import gidpublish.extensions
from gidpublish.utility.exceptions import ExtensionAlreadyRegisteredError, ExtensionLoadError
# endregion[Imports]

# region [TODO]

# TODO: Documentation!!!!


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


class GidpublishBuilder:
    extensions_folder = gidpublish.extensions.EXTENSION_DIR
    extension_base_import_path = "gidpublish.extensions."
    registered_tools_json_file = pathmaker(THIS_FILE_DIR, 'registered_tools.json')

    def __init__(self):
        self.tool_shed = []

    def load_registered_tools(self):
        _raw_data = loadjson(self.registered_tools_json_file)
        for item in _raw_data:
            self.tool_shed.append(StoredTool(**item))

    @staticmethod
    def _get_extension_class_and_import_path(path):

        module = import_from_path(path, False)
        spec = spec_from_file_location(remove_extension(path), path)

        return module.register(), spec.parent

    @classmethod
    def _get_ext_paths_copy(cls, path):

        absolute_path = pathmaker(cls.extensions_folder, os.path.basename(path))
        if os.path.isfile(absolute_path):
            os.remove(absolute_path)

        if os.path.isfile(path) is False:
            raise FileNotFoundError(f"not able to find the file '{path}'")
        shutil.copyfile(path, absolute_path)
        invalidate_caches()
        module_reload(gidpublish)
        module_reload(gidpublish.extensions)
        return absolute_path

    @classmethod
    def _save_registered_tool(cls, tool_item: StoredTool):
        save_tool_data = loadjson(cls.registered_tools_json_file)
        save_tool_data.append(tool_item.serialize())
        writejson(save_tool_data, cls.registered_tools_json_file)

    @classmethod
    def register_tool(cls, path, copy: bool = True, standard_tool: bool = False):

        if copy is True:
            absolute_path = cls._get_ext_paths_copy(path)

        else:
            absolute_path = pathmaker(path)

        class_object, import_path = cls._get_extension_class_and_import_path(absolute_path)

        class_name = class_object.__name__
        registered_tool_item = StoredTool(remove_extension(path), absolute_path, import_path, class_name, class_object.config_entries(), class_object.extra_dependencies(), '', standard_tool)
        cls._save_registered_tool(registered_tool_item)


# region[Main_Exec]
if __name__ == '__main__':
    GidpublishBuilder.register_tool(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidPublish\gidpublish\dependencies_tool\dependency_finder_class.py", False, True)

# endregion[Main_Exec]
