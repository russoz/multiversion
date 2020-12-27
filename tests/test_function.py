# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

import pytest

from multiversion import multiversion


def test_function():
    target_var = 1

    def target_func():
        return target_var

    @multiversion(target_func)
    def my_function():
        return "fallback"

    @my_function.condition(lambda v: v == 2)
    def func_eq2():
        return "value 2"

    @my_function.condition(lambda v: v == 3)
    def func_eq3():
        return "value 3"

    @my_function.condition(lambda v: v > 10)
    def func_gt10():
        return "value > 10"

    @my_function.condition(lambda v: v > 20)
    def func_gt10():
        return "value > 20"

    assert my_function() == "fallback"
    target_var = 2
    assert my_function() == "value 2"
    target_var = 3
    assert my_function() == "value 3"
    target_var = 50
    assert my_function() == "value > 10"
    target_var = 8
    assert my_function() == "fallback"


if __name__ == '__main__':
    pytest.main()
