

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
from typing import Union
from datetime import tzinfo, datetime, timezone, timedelta
from functools import wraps, lru_cache, singledispatch, total_ordering, partial
from contextlib import contextmanager
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# * Gid Imports -->

import gidlogger as glog

# * Local Imports -->
from gidpublish.utility.enums import VenvSettingFileTypus

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

DependencyItem = namedtuple("DependencyItem", ['name', 'version'])
PipServerInfo = namedtuple("PipServerInfo", ['url', 'proxy'], defaults=(None,))
FreezeItem = namedtuple("FreezeItem", ['name', 'data', "is_github", "is_personal"], defaults=(False, False))
ASFunctionItem = namedtuple("ASFunctionItem", ['file_name', 'file_path', 'class_name', 'function_name'], defaults=(None, None))
SyntaxHighlightingLanguage = namedtuple("SyntaxHighlightingLanguage", ['name', 'aliases', 'group', 'extensions', 'type'], defaults=(None, None, None))
TemplateItem = namedtuple("TemplateItem", ['template', 'info'])
TemplateMetaInfoItem = namedtuple('TemplateMetaInfoItem', ['name', 'file_name', 'source', 'vars'])
DropdownItem = namedtuple('DropdownItem', ['name', 'description', 'code', 'sub_dropdown'], defaults=(None, None, None))
VenvSettingsFileItem = namedtuple('VenvSettingsFileItem', ['name', 'path', 'content', 'typus'], defaults=(VenvSettingFileTypus.Normal,))


VersionHandleItem = namedtuple('VersionHandleItem', ['get_version', 'write_version'])
CliMappingItem = namedtuple("CliMappingItem", ['typus', 'pattern', 'files'], defaults=(None, None))

# subclassed namedtuples


class VersionItem(namedtuple('VersionItem', ['major', 'minor', 'patch', 'seperator'], defaults=(None, '.'))):
    @property
    def cleaned_values(self):
        _as_list = []
        for field in self._fields:
            if field != 'seperator' and getattr(self, field) is not None:
                _as_list.append(getattr(self, field))
        return _as_list

    @property
    def version_string(self):
        return self.seperator.join(map(str, self.cleaned_values))

    # region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
