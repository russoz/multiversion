# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

from platform import python_version

from distutils.version import LooseVersion
import pytest

from multiversion import multiversion


def test_versions():
    target_var = '1.2.3'

    def target_func():
        return target_var

    @multiversion(target_func, normalizer="strictversion")
    def my_function():
        return "sv v123"

    @my_function.condition_inrange(["2.0.0", "3.0.0"])
    def func_lvgt2():
        return "2 <= lv <3"

    @my_function.condition_gt("13.0.0")
    def func_svgt3():
        return "sv gt v3"

    @my_function.condition_eq("1.2.3")
    def func_eq123():
        return "lv equals 123"

    @my_function.condition_lt("7.5.2")
    def func_gt10():
        return "lv lt v752"

    assert my_function() == "lv equals 123"

    target_var = '2.1.0'
    assert my_function() == "2 <= lv <3"

    target_var = 13.5
    assert my_function() == "sv gt v3"

    target_var = "9.2.4"
    assert my_function() == "sv v123"

    target_var = "6.7"
    assert my_function() == "lv lt v752"


@multiversion(selection_function=python_version, normalizer="version")
def witty_comment():
    return "Whatever python"


@witty_comment.condition_eq('3.6')
def witty36():
    return "3 dot 6 py"


@witty_comment.condition_inrange(['3.8.2', '3.8.6'])
def witty38x():
    return "38x py"


@witty_comment.condition_gt('4.0')
def witty_gt4():
    return "gt4py"


def test_python_versions():
    v = LooseVersion(python_version())
    if v == LooseVersion('3.6'):
        assert witty_comment() == "3 dot 6 py"
    elif LooseVersion('3.8.2') <= v < LooseVersion('3.8.6'):
        assert witty_comment() == "38x py"
    elif v > LooseVersion('4.0'):
        assert witty_comment() == 'gt4py'
    else:
        assert witty_comment() == 'Whatever python'


if __name__ == '__main__':
    pytest.main()
