# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
"""
Module for holding the multiversion decorator.
"""

from functools import wraps

from distutils.version import StrictVersion, LooseVersion


class MultiVersion:
    """
    MultiVersion decorator, allows different versions of the same function to be called,
    depending on some user-defined criteria.
    """
    def __init__(self, selection_function, func, selection_is_method=False, normalizer=None):
        """
        Creates a new MultiVersion decorator
        :param selection_function: function that returns a value to be used in
               selecting the right function or method to run.
        :param func: function or method being decorated.
        :param selection_is_method: flag indicating whether the selection_function is a method of some class.
        :param normalizer: function used to transform the selection values before applying the condition.
        """
        self.selection_function = selection_function
        self.selection_is_method = selection_is_method
        self.normalizer = normalizer
        self._conditions = []
        self.func = func
        self.instance = None

    def __get__(self, instance, owner):
        """
        Descriptor-protocol get, used to save the reference to the object that the method is bound to.
        :param instance: object reference.
        :param owner: class reference, unused in this implementation.
        :return: a reference to our very own decorator.
        """
        self.instance = instance
        return self

    def normalize(self, value):
        """
        If this decorator has a normalizer, convert value with it.
        :param value: a value to be possibly normalized.
        :return: either a normalized value or value itself if normalization is not available.
        """
        if self.normalizer:
            func = self.normalizer
            return func(value)
        return value

    def _determine_func(self):
        """
        Determines the callable to be actually used by the decorator
        by testing the selection function against available conditions.
        :return: a callable to be used under the current conditions
        """
        for condition in self._conditions:
            if condition.check():
                return condition.func
        return self.func

    def __call__(self, *args, **kwargs):
        func = self._determine_func()
        if self.instance:
            return func(self.instance, *args, **kwargs)

        return func(*args, **kwargs)

    def condition(self, assertion):
        """
        Decorates another callable based on a selection condition
        :param assertion: function to test the condition
        :return: a decorated callable
        """
        class Condition:
            """
            Internal class, represents a condition for selecting a specific callable
            """
            def __init__(self, mv, func):
                self.mv = mv
                self.func = func

            def run_assertion(self, value):
                """
                Run the assertion function for a specific value.
                :param value: value to be tested.
                :return: boolean result of the assertion.
                """
                return bool(assertion(self.mv.normalize(value)))

            def check(self):
                """
                Checks whether the selection condition holds true.
                :return: a boolean result of the check.
                """
                instance = self.mv.instance
                target = self.mv.selection_function

                if instance is None:
                    return self.run_assertion(target())
                if isinstance(target, staticmethod):
                    return self.run_assertion(target.__func__())

                return self.run_assertion(target(instance))

        def deco(func):
            self._conditions.append(Condition(self, func))
            return func
        return deco

    def __getattr__(self, item):
        if item.startswith("condition_"):
            opname = item.split("_")[1]
            if opname in ('eq', 'ne', 'gt', 'ge', 'lt', 'le', 'inrange'):
                if opname == 'inrange':
                    def dyn_condition(val):
                        return self.condition(lambda x: self.normalize(val[0]) <= x < self.normalize(val[1]))
                else:
                    def dyn_condition(val):
                        return self.condition(lambda x: getattr(x, "__" + opname + "__")(self.normalize(val)))

                dyn_condition.__name__ = item
                return dyn_condition

        raise AttributeError()


def multiversion(selection_function, selection_is_method=False, normalizer=None):
    """
    Factory for creating MultiVersion decorators
    :param selection_function: function that returns a value to be used in selecting the right function or method to run.
    :param selection_is_method: flag indicating whether the selection_function is a method of some class.
    :param normalizer: function used to transform the selection values before applying the condition.
    :return: decorated function or method
    """
    if normalizer in ('version', 'looseversion', 'loose_version'):
        normalizer = lambda v: LooseVersion(str(v))
    elif normalizer in ('strictversion', 'strict_version'):
        normalizer = lambda v: StrictVersion(str(v))

    def deco(func):
        wrapper = MultiVersion(selection_function,
                               func,
                               selection_is_method=selection_is_method,
                               normalizer=normalizer)
        wraps(func)(wrapper)

        return wrapper

    return deco
