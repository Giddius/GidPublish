

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


# subclassed namedtuples

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
