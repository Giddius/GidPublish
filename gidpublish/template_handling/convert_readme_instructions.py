

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
import logging
import platform
import subprocess
from enum import Enum, Flag, auto
from time import sleep
from pprint import pprint, pformat
from typing import Union
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


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
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson,
                                                   dir_change, linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)


# * Local Imports -->


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

class InstructionsConverter:
    instruction_file_ext = '.instruction'
    title_regex = re.compile(r".*\((?<=level=)(?P<title_level>\d+);?\)")

    def __init__(self, instruction_file):

        self.instruction_file = instruction_file
        self._check_instruction_file()
        self.parsed_instructions = []

    @property
    def instruction_lines(self):
        return readit(self.instruction_file).splitlines()

    def _check_instruction_file(self):
        if os.path.isfile(self.instruction_file) is False:
            raise FileNotFoundError
        if os.path.splitext(self.instruction_file)[1] != self.instruction_file_ext:
            raise TypeError

    def _parse_title(self, line):
        regex_result = self.title_regex.search(line)
        if regex_result:
            title_level = regex_result.groupdict().get('title_level')

    def _parse_text(self, line):
        pass

    def _parse_image(self, line):
        pass

    def _parse_link(self, line):
        pass

    def parse_instructions(self):
        handle_mapping = {'title': self._parse_tile,
                          'text': self._parse_text,
                          'image': self._parse_image,
                          'link': self._parse_link}
        for line in self.instruction_lines:
            line = line.strip()
            for indicator, parse_function in handle_mapping.items():
                if line.startswith(indicator):
                    parse_function(line)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
