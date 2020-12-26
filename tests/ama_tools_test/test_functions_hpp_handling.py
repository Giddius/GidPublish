import pytest
from gidpublish.utility.gidtools_functions import pathmaker, writeit, readit


def test_base_attributes(functions_finder):
    func_holder, base_folder = functions_finder
    assert func_holder.functions_folder == pathmaker(base_folder, 'A3-Antistasi', 'functions')
    assert func_holder.functions_hpp_file == pathmaker(base_folder, 'A3-Antistasi', 'functions.hpp')
    assert func_holder.exclude == []
    assert func_holder.found_functions is None


def test_collect_functions(functions_finder, function_finds):
    func_holder, base_folder = functions_finder
    assert func_holder.found_functions is None

    func_holder.collect_functions()
    assert func_holder.found_functions == function_finds


def test_write(functions_finder, written_functions_hpp):
    func_holder, base_folder = functions_finder
    assert readit(func_holder.functions_hpp_file) == ''
    func_holder.write()
    assert readit(func_holder.functions_hpp_file) == written_functions_hpp


def test_strings(functions_finder, written_functions_hpp):
    func_holder, base_folder = functions_finder
    assert str(func_holder) == written_functions_hpp


def test_add_exclusion_functions_finder(functions_finder):
    func_holder, base_folder = functions_finder
    assert func_holder.exclude == []
    func_holder.add_exclusion('initSnowFall')
    assert func_holder.exclude == ['initsnowfall']
