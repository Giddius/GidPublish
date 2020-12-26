"""
GidPublish
"""


__version__ = "0.1"

from dotenv import load_dotenv
import os
from importlib.metadata import metadata
import platform


os.environ['APP_NAME'] = metadata(__name__).get('name')
