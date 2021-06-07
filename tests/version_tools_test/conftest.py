import pytest
import os
from gidpublish.utility.gidtools_functions import writeit, readit


@pytest.fixture
def fake_package_path():
    path = os.path.abspath(r"tests\fake_package")
    init_path = os.path.join(path, 'fake_gidappdata', '__init__.py')
    with open(init_path, 'r') as f:
        content = f.read()
    yield path
    writeit(init_path, content)


@pytest.fixture
def fake_package_init_content():
    return '''"""
GidAppData provides an Userdata deployment, with appdirs as backendend, but easy access to files saved there. Also provides an option to 'fake' deploy it while still developing
"""

__version__ = '0.1.1'


from gidappdata.standard_appdata import *


# log = logging.getLogger('gidappdata')
'''
