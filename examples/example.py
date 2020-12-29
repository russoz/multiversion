#!/usr/bin/env python

from platform import python_version
from multiversion import multiversion

@multiversion(selection_function=python_version, normalizer="version")
def witty_comment():
    return "'Tis but a flesh wound!"

@witty_comment.condition_inrange(['3.8.2', '3.8.6'])
def witty38x():
    return "38x: Don't panic!"

@witty_comment.condition_gt('3.7.0')
def witty_gt3():
    return "gt37: Here we go again!"

print(witty_comment())
