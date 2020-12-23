

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
from jinja2 import BaseLoader, Environment, FileSystemLoader, PackageLoader
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

from gidpublish.utility.named_tuples import ASFunctionItem

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

THIS_FILE_DIR = pathmaker(os.path.abspath(os.path.dirname(__file__)))
AS_BASE_FOLDER = pathmaker(r"D:\Dropbox\hobby\Modding\Programs\Github\Foreign_Repos\A3-Antistasi\A3-Antistasi")


# endregion[Constants]


class FunctionsHppFinder:
    # template_env = Environment(loader=FileSystemLoader(pathmaker(THIS_FILE_DIR, 'templates')))
    template_env = Environment(loader=PackageLoader('gidpublish', 'arma_tools/templates'))
    antistasi_prefix = 'A3A'
    replacement_table = {}

    def __init__(self, functions_folder, functions_hpp_file, exclude: list = None):
        self.functions_folder = pathmaker(functions_folder)
        self.functions_hpp_file = pathmaker(functions_hpp_file)
        self.exclude = [item.casefold() for item in exclude] if exclude is not None else []
        self.found_functions = None

    def _sort_found_functions(self):
        pass

    def collect_functions(self):
        self.found_functions = {}
        for top_folder in os.scandir(self.functions_folder):
            if os.path.isdir(top_folder.path) is True:
                if top_folder.name not in self.found_functions:
                    self.found_functions[top_folder.name] = []
                for function_file in os.scandir(top_folder.path):
                    path = pathmaker(os.path.basename(self.functions_folder), top_folder.name, function_file.name)
                    class_name = os.path.splitext(function_file.name)[0]
                    if '_' in class_name:
                        class_name = class_name.split('_', 1)[1]
                    function_name = self.antistasi_prefix + '_fnc_' + class_name
                    if function_file.name.casefold() not in self.exclude and class_name.casefold() not in self.exclude:

                        self.found_functions[top_folder.name].append(ASFunctionItem(function_file.name, path, class_name, function_name))

    def write(self):
        if self.found_functions is None:
            self.collect_functions()
        template = self.template_env.get_template('functions.hpp.jinja')
        content = template.render(antistasi_prefix=self.antistasi_prefix, found_functions=self.found_functions)
        _mod_lines = []
        for line in content.splitlines():
            for key, value in self.replacement_table.items():
                if f"class {key} " + "{};" in line:
                    line = f"\n{value}\n{line}"
            _mod_lines.append(line)
        writeit(self.functions_hpp_file, '\n'.join(_mod_lines))


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
