"""
GidPublish
"""


__version__ = "0.1"

from dotenv import load_dotenv
import os
from importlib.metadata import metadata
import platform


THIS_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
old_cd = os.getcwd()
os.chdir(THIS_FILE_DIR)
dev_indicator_env_path = os.path.normpath(os.path.join(THIS_FILE_DIR, '../tools/_project_devmeta.env'))

if os.path.isfile(dev_indicator_env_path):
    load_dotenv(dev_indicator_env_path)
    os.environ['IS_DEV'] = 'true'
os.environ['APP_NAME'] = metadata(__name__).get('name')
os.environ['AUTHOR_NAME'] = metadata(__name__).get('author')
os.environ['BASE_FOLDER'] = THIS_FILE_DIR
os.environ['LOG_FOLDER'] = os.path.join(THIS_FILE_DIR)

os.chdir(old_cd)
