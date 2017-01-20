"""Some common functions used throughout, like opening PDFs, file checking. """


from __future__ import absolute_import
import os
import imp
from distutils.spawn import find_executable
from subprocess import call
from sys import platform as _platform
try:
    from itertools import izip
except ImportError:
    izip = zip


def open_pdf(pdf_filename):
    """Open a PDF file using system's default PDF viewer."""
    if _platform.startswith("linux"):
        # linux
        call(["xdg-open", pdf_filename])
    elif _platform == "darwin":
        # OS X
        call(["open", pdf_filename])
    elif _platform == "win32":
        # Windows
        call(["start", pdf_filename])


def cleanup_filepath(filepath):
    """Resolve any env vars, ~, return absolute path."""
    return os.path.abspath(os.path.expandvars(os.path.expanduser(filepath)))


def get_directory(filepath):
    """Return absolute, full directory of file.

    Resolve any environment vars, ~, sym links(?)
    """
    return os.path.dirname(cleanup_filepath(filepath))


def check_file_exists(filepath):
    """Check if file exists. Can do absolute or relative file paths."""
    return os.path.isfile(cleanup_filepath(filepath))


def check_dir_exists(filepath):
    """Check if directory exists."""
    return os.path.isdir(cleanup_filepath(filepath))


def check_dir_exists_create(filepath):
    """Check if directory exists. If not, create it."""
    if not check_dir_exists(filepath):
        os.makedirs(cleanup_filepath(filepath))


def map_columns_to_dict(fields, line, delim=None):
    """Split up line into fields, storing them in a dict.

    Note that entreis are assumed to start at line[0], and thus
    any extra entries in the line are ignored.

    >>> line = "123:police:999:Higgs"
    >>> fields = ["id", "name", "phone"]
    >>> map_columns_to_dict(fields, line, ":")
    {'id': '123', 'name': 'abc', 'phone': '999'}

    Parameters
    ----------
    fields: list[str]
        List of field names, MUST be in same order as the entries in line.

    line: str
        Line to be split and mapped into dict.

    delim: str, optional
        Optional delimiter to separate columns. Default is greedy
        whitespace, like for split(). For non-greedy whitepsace, use ' '.

    Returns
    -------
    dict {str:str}
        Dict of field names: values
    """
    parts = line.strip().split(delim)[0:len(fields) + 1]
    return {k: v.strip() for k, v in izip(fields, parts)}


def check_program_exists(program):
    """Test if external program can be found.

    Parameters
    ----------
    program : str
        Program name

    Returns
    -------
    bool
        Whether program is in PATH
    """
    return bool(find_executable(program))


def check_module_exists(module):
    """Test if Python module exists.

    Parameters
    ----------
    module : str
        Name of module to check

    Returns
    -------
    bool
        Whether module exists
    """
    try:
        imp.find_module(module)
    except ImportError:
        return False
    return True


def generate_repr_str(obj, ignore=None):
    """Generate a generic string for use in __repr__, with object fields and their value.

    Can optionally ignore chosen fields.

    Parameters
    ----------
    obj : object
        Object to create repr string for
    ignore : list[str], optional
        Optional list of object field names to ignore

    Returns
    -------
    str
        The repr string
    """
    ignore = ignore or []
    args_str = ["%s=%s" % (k, repr(obj.__dict__[k])) for k in obj.__dict__ if k not in ignore]
    return "{}({})".format(obj.__class__.__name__, ", ".join(args_str))
