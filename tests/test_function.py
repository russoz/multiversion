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

    @my_function.condition_eq(3)
    def func_eq3():
        return "value 3"

    @my_function.condition(lambda v: v > 20)
    def _():
        return "value > 10"

    @my_function.condition(lambda v: v > 10)
    def _():
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


def test_condition_op():
    def target_function():
        return 123

    @multiversion(target_function)
    def my_function():
        return 456

    with pytest.raises(AttributeError):
        @my_function.condition_whatever(789)
        def fail_func():
            return 65536


def test_wraps():
    @multiversion(selection_function=lambda: 42)
    def funcky():
        """Something funky is going on"""
        return 123

    assert funcky.__name__ == 'funcky'
    assert funcky.__doc__ == """Something funky is going on"""

    @funcky.condition_eq(42)
    def funcky42():
        """Two bit or not two bit"""
        return 456

    assert funcky.__name__ == 'funcky'
    assert funcky.__doc__ == """Something funky is going on"""


if __name__ == '__main__':
    pytest.main()
