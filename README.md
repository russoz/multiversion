MultiVersion Decorator
======================

## Purpose
The idea for this decorator came from working on writing and reviewing [Ansible](https://www.ansible.com/) modules for
the [community.general](https://github.com/ansible-collections/community.general/) collection. Many times modules need
to provide compatibility with a number of different versions of Python itself, as well as with specific libraries.

Instead of having blocks of code that look like:
```python
v = platform.python_version_tuple()
if v > (2, 7, 0):
    # do something
elif (3,6) <= v < (3,7):
    # do something else
elif v >= (3, 7):
    # yet something else
```
nested at times in multiple levels of indentation, we could have something that promoted a cleaner way to handle these
cases.

So, `multiversion` aims to be a simple, yet powerful mechanism to express that.

## How It Works

The `multiversion` decorator can be used with any kind of user-defined condition, but a most likely use case would be
to run different code for different python versions. To achieve that, a sample snippet would be:
```python
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
```
The outcome will depend on the python version used to execute it:
```shell
$ ./py38/bin/python --version    # Python 3.8.5
$ ./py38/bin/python example.py   # 38x: Don't panic!
$ ./py39/bin/python --version    # Python 3.9.0+
$ ./py39/bin/python example.py   # gt37: Here we go again!
$ ./py36/bin/python --version    # Python 3.6.5
$ ./py36/bin/python example.py   # 'Tis but a flesh wound!
```
The order of the conditions **does matter**: the functions/methods supporting conditionals will be stored in the order they
have been declared. The first one whose condition yields `True` as result will be used.

### Features

* Easy declaration: just add the `multiversion` decorator to a function or a method. The only mandatory argument is
  `selection_function` - a callable that will return the value upon which the function selection will be made.
  * If the `selection_function` is actually a method (a regular one, neither a `staticmethod` nor a `classmethod`),
    then the user must pass `selection_is_method=True`, as the decorator has no way of calculating that.
  * Readily available functions, such as `platform.python_version()` can be used as selection functions.
* Conditions can be easily declared with `@function_name.condition_OP`, where operator OP can be named after any of 
  the standard comparison operators in python: `eq`, `ne`, `gt`, `ge`, `lt`, and `le`.
  * For example: 
    ```python
    from multiversion import multiversion
    
    @multiversion(selection_function=hours_since_start)
    def end_message():
        print("Congratulations you finished!")
    
    @end_message.condition_ge(24.0)
    def _():   # function name does not really matter here
        print("If I knew it would take you this long, I would have ordered a drink.")
    
    @end_message.condition_ge(5.0)
    def _():
        print("C'mon even a F-1 car stops before that.")
        
    @end_message.condition_gt(2.5)
    def _():
        print("Gracious me, you thought this was a marathon?")
    
    @end_message.condition_le(0.75)
    def _():
        print("Woah, no cheating!!")
    ```
* Alternatively, selection function and conditions can be specified using generic functions:
  ```python
  from multiversion import multiversion
  
  @multiversion(selection_function=lambda: to_hours(now() - start_time))
  def end_message():
      print("Congratulations you finished!")
  
  @end_message.condition(lambda v: v > 24.0)
  def _():
      print("If I knew it would take you this long, I would have ordered a drink.")
* Specific or more complex categories can be used for selection values, by using `normalizer`, as in: 
  ```python
  from platform import python_version
  
  from distutils.version import LooseVersion
  from multiversion import multiversion
  
  @multiversion(selection_function=python_version, normalizer=LooseVersion)
  def witty_comment():
      return "'Tis but a flesh wound!"  
  ```
  This means that both the result of the selection function and the arguments to `condition_OP` methods will
  be coerced into `normalizer` first.
  * As a convenience, user can specify plain strings: `version`, `strictversion` (and a couple of
    accompanying aliases for those), that will indicate the use of
    ```python
    lambda x: LooseVersion(str(x))
    lambda x: StrictVersion(str(x))
    ```
  
    as normalizers, respectively.

## Installation

### Standard Procedure
Installation is standard - as soon as this goes into PyPI then it is a matter of simply running:
```shell
$ pip install multiversion
```

### Development Version
To install the development version of the package, clone the repository from:

- https://github.com/russoz/multiversion.git

Then build it with `tox`.

## Contributing

Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) document.

## Disclaimer

This is my first independent, self-contained, python project, built from scratch. This is also working as a platform
for me to get more acquainted with many a number of tools in the python development universe.
