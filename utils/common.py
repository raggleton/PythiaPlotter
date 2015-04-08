"""
Some common functions used throughout, like opening PDFs, file checking
"""

import os
from subprocess import call
from subprocess import check_output
from sys import platform as _platform


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
    """Return absolute, full path of file.
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
        os.makedirs(filepath)
