import pytest
from gidpublish.utility.gidtools_functions import pathmaker, readit
import os
from gidpublish.dependencies_tool import DependencyFinder
from gidpublish.utility.named_tuples import DependencyItem


def test_init(dep_finder, fake_top_module, fake_package_dir, this_dir):
    assert dep_finder.target_dir == pathmaker(fake_top_module)
    assert dep_finder.dependency_excludes == []
    assert dep_finder.ignore_dirs == []
    assert dep_finder.follow_links is True
    assert dep_finder.pypi_server.url == "https://pypi.python.org/pypi/"
    assert dep_finder.pypi_server.proxy is None
    assert dep_finder.dependencies is None
    os.chdir(this_dir)
    new_dep_finder = DependencyFinder(excludes=["uvloop", 'DIScord'],
                                      ignore_dirs=[fake_package_dir, r"C:\Program Files\Python38"],
                                      follow_links=False)
    assert new_dep_finder.target_dir == this_dir
    assert set(new_dep_finder.dependency_excludes) == set(['uvloop', 'discord'])
    assert set(new_dep_finder.ignore_dirs) == set([fake_package_dir, 'C:/Program Files/Python38'])
    assert new_dep_finder.follow_links is False
    assert new_dep_finder.pypi_server.url == "https://pypi.python.org/pypi/"
    assert new_dep_finder.pypi_server.proxy is None
    assert new_dep_finder.dependencies is None


def test_add_excludes(dep_finder):
    assert dep_finder.dependency_excludes == []
    dep_finder.add_excludes('uVloop')
    assert dep_finder.dependency_excludes == ['uvloop']
    dep_finder.add_excludes(['discord', 'appdIRS', 'WeasyPrint'])
    assert set(dep_finder.dependency_excludes) == set(['uvloop', 'discord', 'appdirs', 'weasyprint'])
    dep_finder.add_excludes(dep_finder.clear)
    assert dep_finder.dependency_excludes == []


def test_add_ignore_dirs(dep_finder):
    assert dep_finder.ignore_dirs == []
    dep_finder.add_ignore_dirs(r"C:\Program Files\Python38")
    assert dep_finder.ignore_dirs == ['c:/program files/python38']
    dep_finder.add_ignore_dirs(['C:/something/one', r"C:\something\two"])
    assert set(dep_finder.ignore_dirs) == set(['c:/program files/python38', 'c:/something/one', "c:/something/two"])
    dep_finder.add_ignore_dirs(dep_finder.clear)
    assert dep_finder.ignore_dirs == []


def test_set_target_dir(dep_finder, fake_top_module, this_dir):
    assert dep_finder.target_dir == pathmaker(fake_top_module)
    dep_finder.set_target_dir(this_dir)
    assert dep_finder.target_dir == this_dir
    with pytest.raises(FileExistsError):
        dep_finder.set_target_dir(r"C:\\fantasy\\folder")


def test_gather_dependencies(dep_finder):
    assert dep_finder.dependencies is None
    dep_finder.gather_dependencies()
    assert set(dep_finder.dependencies) == set([DependencyItem(name='appdirs', version='1.4.4'),
                                                DependencyItem(name='click', version='7.1.2'),
                                                DependencyItem(name='gidappdata', version='0.1.1'),
                                                DependencyItem(name='gidconfig', version='0.1.4'),
                                                DependencyItem(name='gidlogger', version='0.1.3'),
                                                DependencyItem(name='python-dotenv', version='0.15.0')])


def test_as_stringlist(dep_finder):
    assert dep_finder.dependencies is None
    assert set(dep_finder.as_stringlist) == set(['appdirs==1.4.4',
                                                 'click==7.1.2',
                                                 'gidappdata==0.1.1',
                                                 'gidconfig==0.1.4',
                                                 'gidlogger==0.1.3',
                                                 'python-dotenv==0.15.0'])
    assert set(dep_finder.dependencies) == set([DependencyItem(name='appdirs', version='1.4.4'),
                                                DependencyItem(name='click', version='7.1.2'),
                                                DependencyItem(name='gidappdata', version='0.1.1'),
                                                DependencyItem(name='gidconfig', version='0.1.4'),
                                                DependencyItem(name='gidlogger', version='0.1.3'),
                                                DependencyItem(name='python-dotenv', version='0.15.0')])
    dep_finder.dependencies = [DependencyItem('test_item_1', '0.0.1'), DependencyItem('test_item_2', '0.0.2')]
    assert set(dep_finder.as_stringlist) == set(['test_item_1==0.0.1',
                                                 'test_item_2==0.0.2'])
    dep_finder.gather_dependencies()
    assert set(dep_finder.as_stringlist) == set(['appdirs==1.4.4',
                                                 'click==7.1.2',
                                                 'gidappdata==0.1.1',
                                                 'gidconfig==0.1.4',
                                                 'gidlogger==0.1.3',
                                                 'python-dotenv==0.15.0'])
    dep_finder.add_excludes(['click', "ApPdIrS"])
    assert set(dep_finder.as_stringlist) == set(['gidappdata==0.1.1',
                                                 'gidconfig==0.1.4',
                                                 'gidlogger==0.1.3',
                                                 'python-dotenv==0.15.0'])


def test_filtered(dep_finder):
    assert dep_finder.dependencies is None
    assert set(dep_finder.filtered) == set([DependencyItem(name='appdirs', version='1.4.4'),
                                            DependencyItem(name='click', version='7.1.2'),
                                            DependencyItem(name='gidappdata', version='0.1.1'),
                                            DependencyItem(name='gidconfig', version='0.1.4'),
                                            DependencyItem(name='gidlogger', version='0.1.3'),
                                            DependencyItem(name='python-dotenv', version='0.15.0')])
    dep_finder.dependencies = [DependencyItem('test_item_1', '0.0.1'), DependencyItem('test_item_2', '0.0.2')]
    assert set(dep_finder.filtered) == set([DependencyItem(name='test_item_1', version='0.0.1'),
                                            DependencyItem(name='test_item_2', version='0.0.2')])
    dep_finder.gather_dependencies()
    assert set(dep_finder.filtered) == set([DependencyItem(name='appdirs', version='1.4.4'),
                                            DependencyItem(name='click', version='7.1.2'),
                                            DependencyItem(name='gidappdata', version='0.1.1'),
                                            DependencyItem(name='gidconfig', version='0.1.4'),
                                            DependencyItem(name='gidlogger', version='0.1.3'),
                                            DependencyItem(name='python-dotenv', version='0.15.0')])
    dep_finder.add_excludes(['click', "ApPdIrS"])
    assert set(dep_finder.filtered) == set([DependencyItem(name='gidappdata', version='0.1.1'),
                                            DependencyItem(name='gidconfig', version='0.1.4'),
                                            DependencyItem(name='gidlogger', version='0.1.3'),
                                            DependencyItem(name='python-dotenv', version='0.15.0')])
    assert set(dep_finder.dependencies) == set([DependencyItem(name='appdirs', version='1.4.4'),
                                                DependencyItem(name='click', version='7.1.2'),
                                                DependencyItem(name='gidappdata', version='0.1.1'),
                                                DependencyItem(name='gidconfig', version='0.1.4'),
                                                DependencyItem(name='gidlogger', version='0.1.3'),
                                                DependencyItem(name='python-dotenv', version='0.15.0')])


def test_to_requirements_file(dep_finder, temp_requirement_file):
    assert dep_finder.dependencies is None
    dep_finder.to_requirements_file(temp_requirement_file)
    assert os.path.isfile(temp_requirement_file) is True
    assert set(readit(temp_requirement_file).splitlines()) == set(dep_finder.as_stringlist)
    old_stringlist = set(dep_finder.as_stringlist)
    dep_finder.add_excludes(['click', "ApPdIrS"])
    dep_finder.to_requirements_file(temp_requirement_file, overwrite=False)
    assert set(readit(temp_requirement_file).splitlines()) == old_stringlist
    dep_finder.to_requirements_file(temp_requirement_file, overwrite=True)
    assert set(readit(temp_requirement_file).splitlines()) == set(dep_finder.as_stringlist)
