"""
Some common functions used throughout, like opening PDFs, file checking.
"""


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


def get_full_path(filepath):
    """Return absolute, full directory of file.
    Resolve any environment vars, ~, sym links(?)"""
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


def map_columns(fields, line, delim=None):
    """Make dict from fields titles and line.

    fields: list of field names, MUST be in same order as the entries in
        line.

    line: line to be split and mapped into dict.

    delim: optional delimiter to separate columns. Default is greedy
        whitespace, like for split(). For non-greedy whitepsace, use ' '.
    """
    parts = line.strip().split(delim)[0:len(fields) + 1]
    return {k: v.strip() for k, v in izip(fields, parts)}


def check_program_exists(program):
    """Test if external program can be found."""
    return bool(find_executable(program))


def check_module_exists(module):
    """Test if Python module exists."""
    try:
        imp.find_module(module)
    except ImportError:
        return False
    return True
