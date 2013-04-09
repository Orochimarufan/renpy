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

Porting progress:
+ renpy
    + __init__.py
    + bootstrap.py
    + config.py
+ modules
    
"""

import sys
import operator
import types

# use this variable to determine wether we're running Py3k
PY3 = sys.version_info >= (3,)

#----------------------------------------------------------------------------
# Unicode related things
if PY3:
    unicode = str
    bytes = bytes
    StringType = str
else:
    unicode = unicode
    bytes = str
    StringType = basestring
str = str

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

# *IOs
if PY3:
    from io import StringIO, BytesIO
    TextIO = StringIO
else:
    from cStringIO import StringIO
    from io import StringIO as TextIO
    BytesIO = StringIO


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

    don't use this if the BaseClass' MetaClass' Constructor modifies __dict__!
    you can either do
        MyClass = MyMetaClass("MyClass", (MyBaseClass,), {...})
    or
        class MyClass(MyMetaClass("MyBaseClass+MyMetaClass", (MyBaseClass,), {})): ...
    while the latter creates an intermediary class, it's probably more comfortable than
    initializing the new class in dict notation
    """
    __slots__ = ("_meta",)

    def __init__(self, metaclass):
        self._meta = metaclass

    def __call__(self, cls):
        return self._meta(cls.__name__, cls.__bases__, dict(cls.__dict__))


#----------------------------------------------------------------------------
# reraise
if PY3:
    def reraise(tp=None, value=None, tb=None):
        if tp is None and value is None and tb is None:
            tp, value, tb = sys.exc_info()
        elif tp is None or value is None:
            raise TypeError("reraise() takes 0, 2 or 3 arguments")
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
else:
    exec("""def reraise(tp=None, value=None, tb=None):
    if tp is None and value is None and tb is None:
        tp, value, tb = sys.exc_info()
    elif tp is None or value is None:
        raise TypeError("reraise() takes 0, 2 or 3 arguments")
    raise tp, value, tb""")

# next
if sys.version_info >= (2, 6):
    next = next
else:
    def next(iterator, default=None):
        try:
            return iterator.next()
        except StopIteration:
            if default is not None:
                return default
            else:
                reraise()

# execfile
if PY3:
    def execfile(fn, evars):
        """ Compile a python source file and execute it """
        return exec(compile(open(fn).read(), fn, 'exec'), evars)
else:
    execfile = execfile

# iteritems
if PY3:
    iteritems = operator.methodcaller("items")
    listitems = lambda seq: list(seq.items())
    iterkeys = operator.methodcaller("keys")
    itervalues = operator.methodcaller("values")
else:
    iteritems = operator.methodcaller("iteritems")
    listitems = operator.methodcaller("items")
    iterkeys = operator.methodcaller("iterkeys")
    itervalues = operator.methodcaller("itervalues")


#----------------------------------------------------------------------------
# Moves taken from Six http://pythonhosted.org/six/
try:
    from importlib import import_module
except ImportError:
    def import_module(name):
        __import__(name)
        return sys.modules[name]


class _MoveDesc(object):
    __slots__ = "name",

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, tp):
        result = self._get()
        setattr(obj, self.name, result)
        return result


class MovedMod(_MoveDesc):
    __slots__ = "name", "mod"

    if PY3:
        def __init__(self, name, old, new=None):
            super(MovedMod, self).__init__(name)
            if new is None:
                self.mod = name
            else:
                self.mod = new
    else:
        def __init__(self, name, old, new=None):
            super(MovedMod, self).__init__(name)
            self.mod = old

    def _get(self):
        return import_module(self.mod)


class MovedAttr(_MoveDesc):
    __slots__ = "name", "mod", "attr"

    if PY3:
        def __init__(self, name, old_mod, new_mod=None, old_attr=None, new_attr=None):
            super(MovedAttr, self).__init__(name)
            if new_mod is None:
                self.mod = name
            else:
                self.mod = new_mod
            if new_attr is None:
                if old_attr is None:
                    self.attr = name
                else:
                    self.attr = old_attr
            else:
                self.attr = new_attr
    else:
        def __init__(self, name, old_mod, new_mod=None, old_attr=None, new_attr=None):
            super(MovedAttr, self).__init__(name)
            self.mod = old_mod
            if old_attr is None:
                self.attr = old_attr
            else:
                self.attr = name

    def _get(self):
        mod = import_module(self.mod)
        return getattr(mod, self.attr)


def put(t, n, *a):
    sys._getframe().f_back.f_locals[n] = t(n, *a)

class _p(types.ModuleType):
    put(MovedAttr, "cStringIO", "cStringIO", "io", "StringIO")
    put(MovedAttr, "filter", "itertools", "builtins", "ifilter", "filter")
    put(MovedAttr, "input", "__builtin__", "builtins", "raw_input", "input")
    put(MovedAttr, "map", "itertools", "builtins", "imap", "map")
    put(MovedAttr, "reload_module", "__builtin__", "imp", "reload")
    put(MovedAttr, "reduce", "__builtin__", "functools")
    put(MovedAttr, "StringIO", "StringIO", "io")
    put(MovedAttr, "xrange", "__builtin__", "builtins", "xrange", "range")
    put(MovedAttr, "zip", "itertools", "builtins", "izip", "zip")

    put(MovedMod, "builtins", "__builtin__")
    put(MovedMod, "configparser", "ConfigParser")
    put(MovedMod, "copyreg", "copy_reg")
    put(MovedMod, "http_cookiejar", "cookielib", "http.cookiejar")
    put(MovedMod, "http_cookies", "Cookie", "http.cookies")
    put(MovedMod, "http_client", "httplib", "http.client")
    put(MovedMod, "html_entities", "htmlentitydefs", "html.entities")
    put(MovedMod, "html_parser", "HTMLParser", "html.parser")
    put(MovedMod, "email_mime_multipart", "email.MIMEMultipart", "email.mime.multipart")
    put(MovedMod, "email_mime_text", "email.MIMEText", "email.mime.text")
    put(MovedMod, "email_mime_base", "email.MIMEBase", "email.mime.base")
    put(MovedMod, "http_server_base", "BaseHTTPServer", "http.server")
    put(MovedMod, "http_server_cgi", "CGIHTTPServer", "http.server")
    put(MovedMod, "http_server_simple", "SimpleHTTPServer", "http.server")
    put(MovedMod, "cPickle", "cPickle", "pickle")
    put(MovedMod, "queue", "Queue")
    put(MovedMod, "reprlib", "repr")
    put(MovedMod, "socketserver", "SocketServer")
    put(MovedMod, "winreg", "_winreg")
#Tkinter
    put(MovedMod, "tkinter", "Tkinter")
    put(MovedMod, "tkinter_dialog", "Dialog", "tkinter.dialog")
    put(MovedMod, "tkinter_filedialog", "FileDialog", "tkinter.filedialog")
    put(MovedMod, "tkinter_scrolledtext", "ScrolledText", "tkinter.scrolledtext")
    put(MovedMod, "tkinter_simpledialog", "SimpleDialog", "tkinter.simpledialog")
    put(MovedMod, "tkinter_tix", "Tix", "tkinter.tix")
    put(MovedMod, "tkinter_constants", "Tkconstants", "tkinter.constants")
    put(MovedMod, "tkinter_dnd", "Tkdnd", "tkinter.dnd")
    put(MovedMod, "tkinter_colorchooser", "tkColorChooser", "tkinter.colorchooser")
    put(MovedMod, "tkinter_commondialog", "tkCommonDialog", "tkinter.commondialog")
    put(MovedMod, "tkinter_tkfiledialog", "tkFileDialog", "tkinter.filedialog")
    put(MovedMod, "tkinter_font", "tkFont", "tkinter.font")
    put(MovedMod, "tkinter_messagebox", "tkMessageBox", "tkinter.messagebox")
    put(MovedMod, "tkinter_tksimpledialog", "tkSimpleDialog", "tkinter.simpledialog")
#Urllib
    put(MovedMod, "urllib_robotparser", "robotparser", "urllib.robotparser")
    put(MovedAttr, "urllib_urlopen", "urllib2", "urllib.request", "urlopen")
    put(MovedAttr, "urllib_Request", "urllib2", "urllib.request", "Request")

del put

def add_move(move):
    setattr(_p, move.name, move)

def rm_move(name):
    delattr(_p, name)

p = _p(__name__+".p")

