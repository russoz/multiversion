# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

import pytest

from multiversion import multiversion


def test_method():
    target_var = 1

    class A(object):
        def target_method(self):
            return target_var

        @multiversion(target_method, target_is_method=True)
        def my_method(self):
            return "fallback"

        @my_method.condition(lambda v: v == 2)
        def method_eq2(self):
            return "value 2"

        @my_method.condition(lambda v: v == 3)
        def method_eq3(self):
            return "value 3"

        @my_method.condition(lambda v: v > 10)
        def method_gt10(self):
            return "value > 10"

        @my_method.condition(lambda v: v > 20)
        def method_gt10(self):
            return "value > 20"

    a = A()
    assert a.my_method() == "fallback"
    target_var = 2
    assert a.my_method() == "value 2"
    target_var = 3
    assert a.my_method() == "value 3"
    target_var = 50
    assert a.my_method() == "value > 10"
    target_var = 8
    assert a.my_method() == "fallback"


def test_staticmethod_target():
    target_var = 1

    class A(object):
        @staticmethod
        def target_func():
            return target_var

        @multiversion(target_func)
        def my_method(self):
            return "fallback"

        @my_method.condition(lambda v: v == 2)
        def method_eq2(self):
            return "value 2"

        @my_method.condition(lambda v: v == 3)
        def method_eq3(self):
            return "value 3"

        @my_method.condition(lambda v: v > 10)
        def method_gt10(self):
            return "value > 10"

        @my_method.condition(lambda v: v > 20)
        def method_gt10(self):
            return "value > 20"

    a = A()
    assert a.my_method() == "fallback"
    target_var = 2
    assert a.my_method() == "value 2"
    target_var = 3
    assert a.my_method() == "value 3"
    target_var = 50
    assert a.my_method() == "value > 10"
    target_var = 8
    assert a.my_method() == "fallback"


if __name__ == '__main__':
    pytest.main()
