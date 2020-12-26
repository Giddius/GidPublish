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
from jinja2 import BaseLoader, Environment, FileSystemLoader
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

from gidpublish.make_readme_tool.markdown_parts.basic.base_parts import BaseMarkdownStringFormatter
from gidpublish.make_readme_tool.markdown_parts.support.available_syntax_highlighting import LanguageHolder
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

Languages = LanguageHolder()

# endregion[Constants]


class CodeBlock(BaseMarkdownStringFormatter):
    tab_char = '\t'

    def __init__(self, data, language: SyntaxHighlightingLanguage = None, indent=0):
        self.language = Languages.python if language is None else language
        self.md_symbol = "```"
        self.indent = indent
        super().__init__(data)

    @property
    def md_symbol_start(self):
        return f"{self.md_symbol}{self.language.name}\n{self.tab_char*self.indent}"

    @property
    def md_symbol_end(self):
        return f"\n{self.md_symbol}"


class BlockQuote(BaseMarkdownStringFormatter):
    def __init__(self, data):
        self.raw_data = data.splitlines()
        self.data = ""
        if len(self.raw_data) == 1:
            self.data = f'{self.md_symbol_start} {self.raw_data[0]}'
        else:
            for line in self.raw_data:
                self.data += f'{self.md_symbol_start} {line}{self.md_symbol_end}'

    @property
    def md_symbol_start(self):
        return ">"

    @property
    def md_symbol_end(self):
        return "\n"


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
