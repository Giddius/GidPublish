import os


EXTENSION_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.islink(EXTENSION_DIR) is True:
    EXTENSION_DIR = os.readlink(EXTENSION_DIR).replace('\\\\?\\', '')
