"""
GidPublish
"""


__version__ = "0.1.0"


import os
from .version_tools.version_handling import VersionManager, VersionItem, PythonFlitVersionHandler

THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
