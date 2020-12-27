# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

from platform import python_version

from distutils.version import StrictVersion, LooseVersion


class MultiVersionCallable(object):
    """
    MultiVersion decorator, allows different versions of the same function to be called, depending on some
    user-defined criteria.
    """
    class Condition(object):
        def __init__(self, target, assertion, func):
            self.target = target
            self.assertion = assertion
            self.func = func

        def check(self, target_self):
            a = self.assertion
            t = self.target
            if target_self is None:
                return bool(a(t()))
            elif isinstance(t, staticmethod):
                return bool(a(t.__func__()))
            else:
                return bool(a(t(target_self)))

    def __init__(self, target, func, target_is_method=False):
        self.target = target
        self.target_is_method = target_is_method
        self._conditions = []
        self.func = func
        self.instance = None

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def _determine_func(self):
        for condition in self._conditions:
            if condition.check(self.instance):
                return condition.func
        return self.func

    def __call__(self, *args, **kwargs):
        func = self._determine_func()
        if self.instance:
            return func(self.instance, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    def condition(self, assertion):
        def deco(f):
            self._conditions.append(MultiVersionCallable.Condition(self.target, assertion, f))
            return f
        return deco


def multiversion(target, target_is_method=False):
    def deco(func):
        wrapper = MultiVersionCallable(target, func, target_is_method)
        return wrapper
    return deco


def version_condition(op, v, strict=False):
    vcls = StrictVersion if strict else LooseVersion
    ops = dict(
        gt=lambda x: vcls(str(x)) > vcls(str(v)),
        ge=lambda x: vcls(str(x)) >= vcls(str(v)),
        lt=lambda x: vcls(str(x)) < vcls(str(v)),
        le=lambda x: vcls(str(x)) <= vcls(str(v)),
        eq=lambda x: vcls(str(x)) == vcls(str(v)),
        ne=lambda x: vcls(str(x)) != vcls(str(v)),
        inrange=lambda x: vcls(str(v[0])) <= vcls(str(x)) < vcls(str(v[1]))
    )
    return ops[op]


def python_version():
    return LooseVersion(python_version())
