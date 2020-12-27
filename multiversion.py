# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>

from distutils.version import StrictVersion, LooseVersion


class MultiVersionCallable(object):
    """
    MultiVersion decorator, allows different versions of the same function to be called, depending on some
    user-defined criteria.
    """
    def __init__(self, target, func, target_is_method=False, normalizer=None):
        self.target = target
        self.target_is_method = target_is_method
        self.normalizer = normalizer
        self._conditions = []
        self.func = func
        self.instance = None

    def __get__(self, instance, owner):
        self.instance = instance or owner
        return self

    def normalize(self, value):
        if self.normalizer:
            f = self.normalizer
            return f(value)
        return value

    def _determine_func(self):
        for condition in self._conditions:
            if condition.check():
                return condition.func
        return self.func

    def __call__(self, *args, **kwargs):
        func = self._determine_func()
        if self.instance:
            return func(self.instance, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    def condition(self, assertion):
        class Condition(object):
            def __init__(self, mvcallable, func):
                self.mvcallable = mvcallable
                self.func = func

            def run_assertion(self, x):
                return bool(assertion(self.mvcallable.normalize(x)))

            def check(self):
                instance = self.mvcallable.instance
                target = self.mvcallable.target

                if instance is None:
                    return self.run_assertion(target())
                elif isinstance(target, staticmethod):
                    return self.run_assertion(target.__func__())
                else:
                    return self.run_assertion(target(instance))

        def deco(f):
            self._conditions.append(Condition(self, f))
            return f
        return deco

    def __getattr__(self, item):
        if item.startswith("condition_"):
            opname = item.split("_")[1]
            if opname not in ('eq', 'ne', 'gt', 'ge', 'lt', 'le', 'inrange'):
                return

            if opname == 'inrange':
                def dyn_condition(val):
                    return self.condition(lambda x: self.normalize(val[0]) <= x < self.normalize(val[1]))
            else:
                def dyn_condition(val):
                    return self.condition(lambda x: getattr(x, "__" + opname + "__")(self.normalize(val)))

            dyn_condition.__name__ = item
            return dyn_condition


def multiversion(target, target_is_method=False, normalizer=None):
    if normalizer in ('version', 'looseversion', 'loose_version'):
        normalizer = lambda v: LooseVersion(str(v))
    elif normalizer in ('strictversion', 'strict_version'):
        normalizer = lambda v: StrictVersion(str(v))

    def deco(func):
        wrapper = MultiVersionCallable(target, func, target_is_method=target_is_method, normalizer=normalizer)
        return wrapper
    return deco

