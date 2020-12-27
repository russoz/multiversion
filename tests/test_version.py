# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

import pytest
from distutils.version import StrictVersion, LooseVersion

from multiversion import multiversion, version_condition, python_version


def test_versions():
    target_var = '1.2.3'

    def target_func():
        return target_var

    @multiversion(target_func)
    def my_function():
        return "sv v123"

    @my_function.condition(version_condition("inrange", ("2.0.0", "3.0.0")))
    def func_lvgt2():
        return "2 <= lv <3"

    @my_function.condition(version_condition("gt", "13.0.0", strict=True))
    def func_svgt3():
        return "sv gt v3"

    @my_function.condition(version_condition("eq", "1.2.3"))
    def func_eq123():
        return "lv equals 123"

    @my_function.condition(version_condition("lt", "7.5.2"))
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


if __name__ == '__main__':
    pytest.main()
