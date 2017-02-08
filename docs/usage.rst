*****
Usage
*****

Running the program requires the user to (1) select a suitable parser for their input, and (2) a printer.

To show all options, do ``PythiaPlotter -h``.

Input Parsers
=============

There are a variety of acceptable input sources. The input format should be specified using the ``--inputFormat <FORMAT>`` flag.

Pythia8 STDOUT ``PYTHIA``
--------------------------

This is the full event listing output to screen when running Pythia 8.
The user should pipe this into a file, and then pass that file to PythiaPlotter.

LHE ``LHE``
-----------


HepMC ``HEPMC``
---------------


CMSSW ParticleListDrawer ``CMSSW``
----------------------------------

This is the output from the ParticleListDrawer module used in CMSSW.
The user should pipe the output into a file, and then pass that file to PythiaPlotter.

Heppy ``HEPPY``
---------------

This reads in a ROOT file, with branches produced by a custom analyzer module to add in genparticle and mother/daughter info.

Common Parser options
---------------------

- ``-n, --eventNumber``: specify the index of the event to parse in the input file. By default, it will parse the first event (0).

Output Printers
===============

Currently supported printers (specify via ``-p, --printer``):

dot ``DOT``
-----------

This prints a static document using Graphviz.
By default it makes a PDF using the ``dot`` layout program, however the user is free to specify the layout program (via ``--layout <LAYOUT>``) and the output format (via ``--outputFormat <FORMAT>``).

web ``WEB``
-----------

This creates an interactive webpage using Graphviz + vis.js.
By default, it uses the ``dot`` layout program, however the user can change this via the ``--layout <LAYOUT>`` flag.

Common Printer Options
----------------------

There are several options that apply to both printers.

- ``-O, --output <FILENAME>``: specify output filename.
- ``--open``: automatically open the output file once done.
- ``--title <TITLE>``: can optionally put a title on the plot. Note that by default the input file and event number are automatically included.
- ``--redundants``: by default the program removes chains of the same particle that are used internally by the MC generators. To keep these chains, use this flag.
- ``--saveGraphviz``: this allows you to save the graph in a format suitable for parsing by graphviz. The user can then modify settings, etc in the file and ismply run graphviz over it, without having to rerun the entire program.
- ``-r, --representation {NODE, EDGE}``: specify the output particle representation. For more info, see :doc:`Graphs and representations </graphs_representations>`.


Configuring Parsers & Printers
==============================

Although many options can be configured on the command line, some require more
complex settings, or alternatively can be "set-and-forget".
This is done using a config file.
