********************
Notes for developers
********************

.. note::
    There is a makefile with handy targets for running tests, etc - use ``make list`` to show these.

Setup
=====

One should install PythiaPlotter in "editable" mode using pip.
This is easily done using ``make installe`` (note the **e**), or
``make reinstalle`` to uninstall and reinstall.

Developers should install the packages in ``tests/requirements.txt`` for
running the tests, and ``docs/requirements.txt`` for making the docs:

::

    pip install docs/requirements.txt
    pip install tests/requirements.txt

Design Notes
============

The program is designed to be easy to extend in the event that more support
needs to be added for different input or output formats.
Because of this, there is a strong divide between the **parsing**
part of the program, and the **plotting/printing** part.

These two parts communicate by exchanging an ``Event`` object,
which contains a NetworkX ``MultiDiGraph`` object that holds the graph structure and particles.

In addition, there is a divide between the physical objects in an event,
and the structure that connects them. This offers several advantages:

* uniform way to access particle relationships regardless of input or output mode
* separation of physical particle attributes from graph structure and attributes (e.g. parent nodes, etc)
* separation of visual attributes from physical attributes.

The last point is important: this way, we can easily assign a ``NodeAttr``
object to each node, and an ``EdgeAttr`` to each edge, to hold the display
options and decouple the visual attributes from the physical attributes.
By sub-classing those ``*Attr`` objects for different output formats,
we can easily implement a new output format without interference with other output formats.


Testing
=======

There are various make targets to run tests easily:

* ``make test``: run unit tests
* ``make test-examples``: run full execution of the program, for a variety of input options
* ``make cov``: run coverage.py and make a HTML report
* ``make benchmark``: run performance metrics (mostly timing of components)

There are also various targets for linting, etc:

* ``make lint``: run pylint
* ``make lint-py3``: run pylint's python3 checker **Note this is not perfect!**
* ``make flake``: run flake8

Docs can be made locally by doing ``make docs``.

Conventions / Style
===================

Lines should be < 100 lines, but sometimes going over makes more sense than horrible linebreaks.
Try and fix all linter errors/warnings, but sometimes they are silly.
Use `Numpy-style <https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_ for docstrings.
All code should be compatible with python 2.7 and >=3.4.
The compatibilty with 2.7 is because a significant proportion of HEP is still
forced to use it, but at the same time we should forsee migration to python 3.

