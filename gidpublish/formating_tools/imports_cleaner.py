"""
[summary]

[extended_summary]
"""


# region [Imports]
import gc
import os
import re
import sys
import json
import lzma
import time
import queue
import base64
import pickle
import random
import shelve
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import unicodedata
from io import BytesIO
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import Union, Callable, Iterable, Union, List, Tuple, Dict, Set, Optional, TYPE_CHECKING, Generator
from inspect import stack, getdoc, getmodule, getsource, getmembers, getmodulename, getsourcefile, getfullargspec, getsourcelines
from zipfile import ZipFile
from datetime import tzinfo, datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from rich import print as rprint, inspect as rinspect
# * Third Party Imports --------------------------------------------------------------------------------->
import toml
import inspect
import isort
import autopep8
import autoflake
from copy import deepcopy
# * Gid Imports ----------------------------------------------------------------------------------------->
import gidlogger as glog

# * Local Imports --------------------------------------------------------------------------------------->
from gidpublish.utility.file_system_walk import StartsWith, filesystem_walker_files
from gidpublish.utility.gidtools_functions import (readit, clearit, readbin, writeit, loadjson, pickleit, writebin, pathmaker, writejson, dir_change,
                                                   linereadit, get_pickled, ext_splitter, appendwriteit, create_folder, from_dict_to_file)
from abc import ABC, ABCMeta, abstractmethod
from functools import reduce
import operator
from hashlib import blake2b
from weakref import WeakValueDictionary
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from rich.console import Console
from rich.tree import Tree
import os
import pathlib
import sys
import toml
import tomlkit
from benedict import benedict
from gidpublish.utility.misc import recursive_dir_tree
from gidpublish.utility.general_decorators import debug_timing_print

# endregion[Imports]

# region [TODO]

# TODO: pass pyproject toml variables to the sorters

# endregion [TODO]

# region [AppUserData]


# endregion [AppUserData]

# region [Logging]

log = glog.aux_logger(__name__)
log.info(glog.imported(__name__))

# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))

SETTINGS = None
os.environ['IS_DEV'] = 'true'
# endregion[Constants]


def folder_size(folder_path: Union[os.PathLike, str]) -> int:
    all_sizes = []
    for item in os.scandir(folder_path):
        if item.is_file():
            all_sizes.append(item.stat().st_size)
        elif item.is_dir():
            all_sizes.append(folder_size(item.path))
    if all_sizes:
        return reduce(operator.add, all_sizes)
    else:
        return 0


def folder_modification_time(folder_path: Union[os.PathLike, str]) -> datetime:
    all_times = [datetime.fromtimestamp(os.stat(folder_path).st_mtime)]
    for item in os.scandir(folder_path):
        if item.is_file():
            all_times.append(datetime.fromtimestamp(item.stat().st_mtime))
        elif item.is_dir():
            all_times.append(folder_modification_time(item.path))
    return max(all_times)


class UnknownFileTypeError(Exception):

    def __init__(self, path: Union[os.PathLike, str]):
        self.path = pathmaker(path)
        self.name = os.path.basename(self.path)
        self.dir_path = pathmaker(os.path.dirname(self.path))
        self.msg = f"Unable to determine file type for file '{self.name}' in '{self.dir_path}'"
        super().__init__(self.msg)


class BaseTaskTooling(ABC):

    @classmethod
    @property
    @abstractmethod
    def setting_name(cls):
        ...


class RichMixin:

    def __rich__(self) -> str:
        def attribute_select_checker(attr_name: str, attr_object) -> bool:
            if attr_name.startswith('_'):
                return False
            if attr_name.endswith('_'):
                return False
            if inspect.ismethod(attr_object) is True:
                return False

            return True
        c_name = self.__class__.__name__
        spacing = ' ' * (len(c_name) + 1)
        attribute_list = f',\n{spacing}'.join(f"[bold blue]{name}[/bold blue]=[italic]{str(value)}[/italic]" for name, value in inspect.getmembers(self) if attribute_select_checker(name, value) is True)
        return f"[underline green]{c_name}[/underline green](\n{spacing}{attribute_list}\n{spacing})"


class ProjectItemBase(os.PathLike):
    item_factory = None

    @classmethod
    @property
    @abstractmethod
    def is_dir(cls) -> bool:
        ...

    def __init__(self, path: Union[os.PathLike, str]) -> None:
        if self.item_factory is None:
            raise AttributeError("Attribute 'item_factory' is not set")
        self.path = path
        self.name = os.path.basename(self.path)

    @cached_property
    def parent_folder(self) -> "ProjectFolderItem":
        return self.item_factory.get_item(pathmaker(os.path.dirname(self.path)))

    @property
    @abstractmethod
    def size(self) -> int:
        ...

    @property
    @abstractmethod
    def modifed_last_at(self) -> datetime:
        ...

    @cached_property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(os.stat(self.path).st_ctime)

    def __fspath__(self) -> str:
        return str(self.path)

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    def __hash__(self) -> int:
        return hash(self.path)


class ProjectFileItemBase(ProjectItemBase):
    is_dir = False
    encoding = 'utf-8'

    @classmethod
    @property
    @abstractmethod
    def check_preference_position(cls) -> int:
        ...

    def __init__(self, path: Union[os.PathLike, str]) -> None:
        super().__init__(path)
        self.extension = self.name.split('.')[-1]

    @classmethod
    @abstractmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        ...

    @property
    def size(self) -> int:
        return os.stat(self.path).st_size

    @property
    def modifed_last_at(self) -> datetime:
        return datetime.fromtimestamp(os.stat(self.path).st_mtime)

    def get_content(self):
        with open(self.path, 'r', encoding=self.encoding, errors='ignore') as f:
            return f.read()

    def write(self, new_content):
        with open(self.path, 'w', encoding=self.encoding, errors='ignore') as f:
            f.write(new_content)


class ProjectFolderItem(ProjectItemBase):
    is_dir = True

    @property
    def size(self) -> int:
        return folder_size(self.path)

    @property
    def modifed_last_at(self) -> datetime:
        return folder_modification_time(self.path)

    def get_folder_content(self, recursive: bool = False) -> Generator[Union["ProjectFolderItem", ProjectFileItemBase], None, None]:
        for item in os.scandir(self.path):
            if item.is_file():
                yield self.item_factory.get_item(item.path)
            elif item.is_dir():
                folder_item = self.item_factory.get_item(item.path)
                yield folder_item
                if recursive is True:
                    yield from folder_item.get_items(recursive=recursive)

    def get_file(self, file_name: str, nullable: bool = False) -> ProjectFileItemBase:
        for item in self.get_folder_content(False):
            if item.is_dir is False and item.name.casefold() == file_name.casefold():
                return item
        if nullable is False:
            raise FileNotFoundError(file_name)


class DefaultFileItem(ProjectFileItemBase):
    check_preference_position = 100

    @classmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        return True


class JsonFileItem(ProjectFileItemBase):
    check_preference_position = 10

    @classmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        return os.path.splitext(path)[-1].strip('.') == 'json'

    def get_content(self):
        return loadjson(self.path)

    def write(self, new_content):
        writejson(new_content, self.path)


class PythonFileItem(ProjectFileItemBase):
    check_preference_position = 10

    @classmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        return os.path.splitext(path)[-1].strip('.') == 'py'


class PythonInitFileItem(PythonFileItem):
    check_preference_position = 9

    @classmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        return os.path.basename(path).casefold() == '__init__.py'


class TomlFileItem(ProjectFileItemBase):
    check_preference_position = 10

    @classmethod
    def check_if_type(cls, path: Union[os.PathLike, str]) -> bool:
        return os.path.splitext(path)[-1].strip('.') == 'toml'

    def get_content(self):
        return toml.load(self.path)

    def write(self, new_content):
        with open(self.path, 'w') as f:
            f.write(tomlkit.dumps(new_content))


class ProjectFactoryMeta(type):

    def __str__(cls):
        return cls.__name__

    def __repr__(cls):
        return cls.__name__


class ProjectItemFactory(metaclass=ProjectFactoryMeta):
    stored_items = {}
    file_base_class = ProjectFileItemBase
    folder_base_class = ProjectFolderItem
    default_file_item = DefaultFileItem
    _concrete_project_file_classes = None

    @classmethod
    def _get_subclasses_recursive(cls, klass):
        if klass.__subclasses__():
            for subklass in klass.__subclasses__():
                yield from cls._get_subclasses_recursive(subklass)
        if klass is not cls.file_base_class and klass is not cls.default_file_item:
            yield klass

    @classmethod
    @property
    def concrete_project_file_classes(cls) -> List[ProjectFileItemBase]:
        if cls._concrete_project_file_classes is None:
            cls._concrete_project_file_classes = sorted(cls._get_subclasses_recursive(cls.file_base_class), key=lambda x: x.check_preference_position)

        return cls._concrete_project_file_classes

    @classmethod
    def get_item(cls, path: Union[os.PathLike, str]) -> Union[ProjectFolderItem, ProjectFileItemBase]:

        path = pathmaker(path)

        try:
            return cls.stored_items[path.casefold()]
        except KeyError:
            pass

        item = None
        if os.path.isfile(path):
            for concrete_class in cls.concrete_project_file_classes:
                if concrete_class.check_if_type(path) is True:
                    item = concrete_class(path=path)
                    break

            if item is None:
                item = cls.default_file_item(path)

        if os.path.isdir(path):
            item = cls.folder_base_class(path)

        cls.stored_items[path.casefold()] = item
        return item


class ImportsCleaner(BaseTaskTooling):
    setting_name = 'import_cleaner'
    import_region_regex_pattern = (r"""
                                    (?P<startline>\#\s*region\s*\[{import_region_name}\]\n?)
                                    (?P<content>.*?)
                                    (?P<endline>\n\#\s*endregion\s*\[{import_region_name}\]\n?)
                                    """, re.IGNORECASE | re.DOTALL | re.VERBOSE)

    def __init__(self, project) -> None:
        self.project = project
        self.import_region_name = self.project.settings.gidpublish.import_cleaner.import_region_name
        self.run_isort = self.project.settings.gidpublish.import_cleaner.run_isort
        self.run_autoflake = self.project.settings.gidpublish.import_cleaner.run_autoflake

    @cached_property
    def import_region_regex(self) -> re.Pattern:
        pattern, re_enums = self.import_region_regex_pattern
        return re.compile(pattern.format(import_region_name=self.import_region_name), re_enums)

    def process_all(self):
        if self.project.settings.gidpublish.general.concurrency is not None:
            executor = ThreadPoolExecutor if self.project.settings.gidpublish.general.concurrency.casefold() == "threads" else ProcessPoolExecutor
            with executor() as pool:
                list(pool.map(self.process_file, self.project.get_files_for(self)))
        else:
            for file_item in self.project.get_files_for(self):
                self.process_file(file_item)

    def process_file(self, file_item):
        old_content = file_item.get_content()
        imports_section_match = self.import_region_regex.search(old_content)
        if imports_section_match:
            import_statements = '\n'.join(line for line in imports_section_match.group('content').splitlines() if line != '' and not line.strip().startswith('#'))
            new_import_section = imports_section_match.group('startline') + 'n' + import_statements + '\n' + imports_section_match.group("endline")
            new_content = self.import_region_regex.sub(new_import_section, old_content)
            file_item.write(new_content)


class SettingsTypus(Enum):
    TOML = auto()


DEFAULT_SETTINGS = {
    "gidpublish": {
        'general': {'concurrency': 'threads'},
        'project': {
            'files_to_exclude': [],
            'folders_to_exclude': ['.venv', '.git', '.pytest_cache', '__pycache__', '.vscode', 'tests'],
        },
        'import_cleaner': {
            'import_region_name': "imports",
            'run_isort': True,
            'run_autoflake': True
        }
    }
}


class SettingSection:

    def __init__(self, data) -> None:
        self.data = data
        for key, value in self.data.items():
            attr_key = key.replace('-', '_')
            att_value = self.__class__(value) if isinstance(value, dict) else value
            setattr(self, attr_key, att_value)


class Settings:
    default_settings = DEFAULT_SETTINGS

    def __init__(self, root: ProjectFolderItem):
        self.root = root
        self.file = None
        self.typus = None
        self.data = None
        self.collect_settings()

    def collect_settings(self):
        settings_file = self.root.get_file('pyproject.toml', True)
        if settings_file is not None:
            self.file = settings_file
            self.typus = SettingsTypus.TOML
            self.data = self.default_settings | settings_file.get_content().get('tool')
            for key, value in self.data.items():
                setattr(self, key, SettingSection(value))

    def get_value(self, section: str, settings_name: str, key_name: str):
        section = getattr(self, section)
        return section.get(settings_name, {}).get(key_name)

    def query(self, section: str, name: str):
        section = benedict(getattr(self, section))
        _out = section.search(name, in_keys=True, in_values=False, exact=True, case_sensitive=False)
        if _out:
            return _out[0][2]


class ProjectData:
    file_factory = ProjectItemFactory

    def __init__(self, root_path: Union[os.PathLike, str]) -> None:
        ProjectItemBase.item_factory = self.file_factory
        self.root = self.file_factory.get_item(root_path)
        self.settings = Settings(self.root)
        self.files_to_exclude = set(self.settings.gidpublish.project.files_to_exclude)
        self.folders_to_exclude = set(self.settings.gidpublish.project.folders_to_exclude)
        self.top_module_name = self.project_name = self.settings.flit.metadata.module
        self.author_name = self.settings.flit.metadata.author

    @property
    def readme_file(self):
        path = pathmaker(self.root, self.settings.flit.metadata.description_file)
        return self.file_factory.get_item(path)

    @property
    def top_module_folder(self):
        path = pathmaker(self.root, self.top_module_name)
        return self.file_factory.get_item(path)

    @property
    def main_script_file(self):
        path = pathmaker(self.top_module_folder, '__main__.py')
        return self.file_factory.get_item(path)

    @property
    def top_init_file(self):
        path = pathmaker(self.top_module_folder, '__init__.py')
        return self.file_factory.get_item(path)

    @property
    def files(self):
        return list(filter(lambda x: x.is_dir is False, self._all_items))

    @property
    def folders(self):
        return list(filter(lambda x: x.is_dir is True, self._all_items))

    @property
    def _all_items(self):
        return list(self._walk_project())

    def _walk_project(self):
        for dirname, folderlist, filelist in os.walk(self.root, topdown=True):
            folderlist[:] = [d for d in folderlist if d.casefold() not in self.folders_to_exclude]
            for folder in folderlist:
                path = pathmaker(dirname, folder)
                yield self.file_factory.get_item(path)
            for file in filelist:
                if file.casefold() not in self.files_to_exclude:
                    path = pathmaker(dirname, file)
                    yield self.file_factory.get_item(path)

    def get_files_for(self, tooling_item: BaseTaskTooling):
        print(type(tooling_item))

    def get_settings_copy(self):
        return NotImplemented

    def print_tree(self):
        tree = Tree(f":open_file_folder: [link file://{self.root}]{self.root}",
                    guide_style="bold bright_blue",)
        recursive_dir_tree(pathlib.Path(self.root), tree, self.files_to_exclude, self.folders_to_exclude)
        _console = Console(soft_wrap=True)
        _console.print(tree)


# region[Main_Exec]
if __name__ == '__main__':

    _root_path = r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidPublish"
    x = ProjectData(_root_path)
    dd = ImportsCleaner(x)


# endregion[Main_Exec]
