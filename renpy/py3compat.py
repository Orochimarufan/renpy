#!/usr/bin/python
# Copyright (c) 2013 Ren'Py Contributors
#
#       Authors: Orochimarufan <orochimarufan.x3@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, unicode_literals

"""
This File is part of Ren'Py.

It contains various tools to create hybrid python 2.x/3.x code.

Guidelines:
- always use "from __future__ import absolute_import"
- use "from __future__ import unicode_literals" where possible
- use py3compat.PY3 to determine if we're running 3.x
- where libraries expect bytes or unicode strings, use b() and u() respectively
- if libraries expect a native string (str), use n()
- avoid names like "String" or "str", they might cause confusion
"""

import sys

# use this variable to determine wether we're running Py3k
PY3 = sys.version_info >= (3,)

#----------------------------------------------------------------------------
# The unicode falback codec
renpy_unicode_codec_fs = sys.getfilesystemencoding() or "utf-8"

# Unicode related things
if PY3:
    unicode = str
    bytes = bytes
    NativeString = str
    StringType = str
else:
    unicode = unicode
    bytes = str
    NativeString = str
    StringType = basestring

# conversion functions
def u(s, codec="utf-8", errors='strict'):
    """ Ensure a unicode string """
    if isinstance(s, unicode):
        return s
    elif isinstance(s, bytes):
        return s.decode(codec, errors)
    else:
        return unicode(s)

def b(s, codec="utf-8", errors='strict'):
    """ Ensure a bytestring """
    if isinstance(s, bytes):
        return s
    elif isinstance(s, unicode):
        return s.encode(codec, errors)
    else:
        return bytes(s)

# "Native Strings" are bytes on py2 and unicode on py3 (i.e. what's called "str" respectively)
if PY3:
    n = u
else:
    n = b

# Check functions
def isstring(s):
    """ Check if something is a string """
    return isinstance(s, StringType)

def isstringish(s):
    """ Same as isstring() on py2, but includes bytes in py3 """
    return isinstance(s, (bytes, unicode))


#----------------------------------------------------------------------------
# Integers/Longs
if PY3:
    IntTypes = (int,)
    int, long = int, int
else:
    IntTypes = (int, long)
    int, long = int, long


#----------------------------------------------------------------------------
# Metaclass definitions
class withmetaclass(object):
    """
    Class decorator to specify metalcasses in a portable way

    @withmetaclass(MyMetaClass)
    class MyClass(MyBaseClass): ...
    """
    __slots__ = ("_meta",)

    def __init__(self, metaclass):
        self._meta = metaclass

    def __call__(self, cls):
        return self._meta(cls.__name__, cls.__bases__, dict(cls.__dict__))


#----------------------------------------------------------------------------
# builtins
if PY3:
    import builtins
else:
    import __builtin__ as builtins

# next
if sys.version_info >= (2, 6):
    next = builtins.next
else:
    def next(iterator, default=None):
        try:
            return iterator.next()
        except StopIteration:
            if default is not None:
                return default
            else:
                raise

# input
if PY3:
    input = input
else:
    input = raw_input

# execfile
if PY3:
    def execfile(fn, evars):
        """ Compile a python source file and execute it """
        return exec(compile(open(fn).read(), fn, 'exec'), evars)
else:
    execfile = execfile

# iteritems
if PY3:
    iteritems = lambda seq: seq.items()
    listitems = lambda seq: list(seq.items())
else:
    iteritems = lambda seq: seq.iteritems()
    listitems = lambda seq: seq.items()


#----------------------------------------------------------------------------
# some libraries
# String/Text/BytesIO
# StringIO is the native StringIO, TextIO always the unicode one
if PY3:
    from io import StringIO, BytesIO
    TextIO = StringIO
else:
    from cStringIO import StringIO
    from io import StringIO as TextIO
    BytesIO = StringIO


# urllib
if PY3:
    from urllib.request import Request, urlopen
else:
    from urllib2 import Request, urlopen

