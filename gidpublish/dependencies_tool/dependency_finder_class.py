

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
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)

from gidpublish.utility.named_tuples import DependencyItem, PipServerInfo
from gidpublish.abstracts.abstract_workjob_interface import AbstractBaseWorkjob
from gidpublish.utility.misc_functions import remove_unnecessary_lines, find_file
from gidpublish.data.general_exclusions import GENERAL_FIXED_EXCLUDE_FOLDERS
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


# endregion[Constants]


class _DependencyFinderEnums(Enum):
    clear = auto()


class DependencyFinder(AbstractBaseWorkjob):
    fixed_excludes = GENERAL_FIXED_EXCLUDE_FOLDERS
    config_section = 'dependency_finder'

    clear = _DependencyFinderEnums.clear
    dependency_item = DependencyItem

    valid_pyproject_specs = ['flit']

    def __init__(self, target_dir, excludes: list = None, ignore_dirs: list = None, follow_links: bool = True):
        self.target_dir = None
        self.set_target_dir(target_dir)
        self.spec_format = 'flit'
        self.dependency_excludes = [excl_item.casefold() for excl_item in excludes] if excludes is not None else []
        self.ignore_dirs = [pathmaker(dir) for dir in ignore_dirs] if ignore_dirs is not None else []
        self.follow_links = follow_links
        self.pypi_server = PipServerInfo("https://pypi.python.org/pypi/", None)
        self.dependencies = None

    @property
    def as_stringlist(self):
        if self.dependencies is None:
            self.gather_dependencies()
        return [f"{item.name}=={item.version}" for item in self.dependencies if item.name.casefold() not in self.dependency_excludes]

    @property
    def filtered(self):
        if self.dependencies is None:
            self.gather_dependencies()
        return [item for item in self.dependencies if item.name.casefold() not in self.dependency_excludes]

    def set_pypi_server(self, url, proxy):
        self.pypi_server = PipServerInfo(url=url, proxy=proxy)

    def add_excludes(self, exclude):
        if isinstance(exclude, str):
            self.dependency_excludes.append(exclude.casefold())
        elif type(exclude) in [list, set, tuple, frozenset]:
            for item in exclude:
                self.dependency_excludes.append(item.casefold())
        elif exclude is self.clear:
            self.dependency_excludes = []
        else:
            raise TypeError(type(exclude))

    def add_ignore_dirs(self, ignore_dir):
        if isinstance(ignore_dir, str):
            self.ignore_dirs.append(pathmaker(ignore_dir).casefold())
        elif type(ignore_dir) in [list, set, tuple, frozenset]:
            for item in ignore_dir:
                self.ignore_dirs.append(pathmaker(item).casefold())
        elif ignore_dir is self.clear:
            self.ignore_dirs = []
        else:
            raise TypeError(type(ignore_dir))

    def _convert_imports_to_namedtuple(self, imports):
        return [self.dependency_item(**item) for item in imports]

    def set_target_dir(self, target_dir):
        target_dir = pathmaker(target_dir)
        if os.path.exists(target_dir) is False:
            raise FileNotFoundError(f'argument "target_dir"("{target_dir}"), does not point to an existing directory')
        self.target_dir = target_dir

    def gather_dependencies(self):
        candidates = pipreqs.get_all_imports(self.target_dir,
                                             encoding=None,
                                             extra_ignore_dirs=self.ignore_dirs,
                                             follow_links=self.follow_links)
        candidates = pipreqs.get_pkg_names(candidates)
        local = pipreqs.get_import_local(candidates, encoding=None)
        difference = [x for x in candidates
                      if x.lower() not in [z['name'].lower() for z in local]]
        imports = local + pipreqs.get_imports_info(difference,
                                                   proxy=self.pypi_server.proxy,
                                                   pypi_server=self.pypi_server.url)
        self.dependencies = self._convert_imports_to_namedtuple(imports)

    def _to_flit_pyproject(self, content):
        content['tool']['flit']['metadata']['requires'] = self.as_stringlist
        return content

    def to_pyproject_file(self, pyproject_file=None):
        if self.spec_format.casefold() not in self.valid_pyproject_specs:
            raise KeyError(f"argument 'spec_format' ('{self.spec_format}') is not a valid specification, see '{str(self)}.valid_pyproject_specs' for possible specifications")

        pyproject_file = find_file(self.target_dir, 'pyproject.toml', self.fixed_excludes, 'file') if pyproject_file is None else pyproject_file
        if pyproject_file is None:
            raise FileNotFoundError("could not located 'pyproject.toml'")
        pyproject_content = toml.load(pyproject_file)
        new_content = getattr(self, f"_to_{self.spec_format.casefold()}_pyproject")(pyproject_content)
        with open(pyproject_file, 'w') as pyproject_output_file:
            toml.dump(new_content, pyproject_output_file)

    def to_requirements_file(self, requirements_file=None, overwrite=True):
        out_file = find_file(self.target_dir, 'requirements.txt', self.fixed_excludes, 'file') if requirements_file is None else requirements_file
        if out_file is None:
            raise FileNotFoundError("could not located 'requirements.txt'")
        if os.path.isfile(out_file) is True:
            if overwrite is False:
                log.warning("Requirements file ('%s') already exists and overwrite is False, aborting writing requirements file", out_file)
                return

            else:
                log.info("Requirements file('%s') already exists and overwrite is True, overwriting requirements file", out_file)

        writeit(out_file, '\n'.join(self.as_stringlist))

    def work(self):
        self.gather_dependencies()
        self.to_pyproject_file()
        self.to_requirements_file()
        log.info('finished work of "%s"', str(self))

    def add_exclusion(self, exclusion_item: Tuple[str, str]):
        if exclusion_item[0] == 'folder':
            self.add_ignore_dirs(exclusion_item[1])
        elif exclusion_item[0] == 'package':
            self.add_excludes(exclusion_item[1])

    @classmethod
    def configure(cls, config):
        pass

    @classmethod
    def config_entries(cls):
        return {'dependency_finder': {'target_dir': '',
                                      'pyproject_file': '',
                                      'requirements_file': '',
                                      'spec_format': 'flit',
                                      'ignore_dirs': '',
                                      'ignore_packages': '',
                                      'follow_links': True}}

    @classmethod
    def extra_dependencies(cls):
        return [('toml', 'pytoml'), ('pipreqs', None)]

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.target_dir)}, {str(self.dependency_excludes)}, {str(self.ignore_dirs)}, {str(self.follow_links)})"


def register():
    return DependencyFinder


# region[Main_Exec]
if __name__ == '__main__':
    x = DependencyFinder(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Gid_Venv\gidvenv")
    x.gather_dependencies()
    for i in x.as_stringlist:
        print(i)
# endregion[Main_Exec]
