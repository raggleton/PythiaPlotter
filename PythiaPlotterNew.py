#!/usr/bin/env python
import os.path
import subprocess
from subprocess import call
from sys import platform as _platform
import argparse
import re
import imp  # For testing if modules exist

# PythiaPlotter files:
import config as CONFIG
import pythiaParser
import hepmcParser
import eventClasses
import nodeWriter
import edgeWriter
import pdfPrinter

# Script that converts the event listing from either Pythia 8 output or
# standard HepMC file into a GraphViz file, which is then plotted with
# either latex (nice particle symbols) or dot (faster, less nice),
# and output as a PDF.
# e.g.
#
# python PythiaPlotter.py
#
# If you want the PDF to open automatically after processing, use --openPDF
#
# This script outputs a GraphViz file and automatically plots it.
# By default, it uses pdflatex and dot2tex(i) to make nice particle names.
#
# Robin Aggleton 2014, robin.aggleton@cern.ch
#
###############################################################################
# DO NOT EDIT ANYTHING BELOW HERE
###############################################################################


# Setup commandline args parser
def get_parser():
    """Define all command-line options. Returns ArgumentParser object"""

    parser = argparse.ArgumentParser(
        description="Convert PYTHIA8 or HepMC event listing into graph using \
        dot/GraphViz/dot2tex/pdflatex"
    )
    # TODO: improve multi-line strings. This sucks!
    parser.add_argument("-i", "--input",
                        help="input text file with Pythia 8 output \
                        (if unspecified, defaults to qcdScatterSmall.txt)",
                        default="qcdScatterSmall.txt")
    parser.add_argument("--inputType",
                        help="input type, either HEPMC or PYTHIA (latter for \
                        the *direct* output from Pythia8 on screen).\
                        If unspecified, will try and make an educated guess,\
                        but could fail!",
                        choices=["HEPMC", "PYTHIA"])
    parser.add_argument("--eventNumber",
                        help="For HepMC file, select event number to plot",
                        type=int, default=0)
    parser.add_argument("-oGV", "--outputGV",
                        help="output GraphViz filename \
                        (if unspecified, defaults to INPUT.gv)")
    parser.add_argument("-oPDF", "--outputPDF",
                        help="output graph PDF filename \
                        (if unspecified, defaults to INPUT.pdf)")
    parser.add_argument("--openPDF",
                        help="automatically open PDF once plotted",
                        action="store_true")
    parser.add_argument("-m", "--mode", choices=["NODE", "EDGE"],
                        help="particle representation on PDF: NODE or EDGE",
                        default="NODE")
    parser.add_argument("--noPDF",
                        help="don't convert to PDF",
                        action="store_true")
    parser.add_argument("--rawNames",
                        help="don't convert particle names to tex, use raw \
                        string names - faster but less pretty",
                        action="store_true")
    parser.add_argument("--StraightEdges",
                        help="use straight edges instead of curvy",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="print debug statements to screen",
                        action="store_true")

    return parser


def check_program_exists(progName):
    """Test if external program runs"""
    try:
        # Storing in string stifles output
        prog_out = subprocess.check_output([progName, "-h"],
                                           stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        args.rawNames = True
        print(cpe.returncode)
        print(cpe.output)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            args.rawNames = True
            print "You need to install " + progName + \
                  "or add it to PATH variable"
            print(e)
        else:
            # Something else went wrong while trying to run `wget`
            print(e)


def check_module_exists(mod):
    """Test if Python module exists"""
    try:
        imp.find_module(mod)
    except ImportError:
        print "!!! Module " + mod + " doesn't exist"
        print "No fancy particle names for you!"
        args.rawNames = True


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

###############################################################################
# MAIN BODY OF CODE HERE
###############################################################################

if __name__ == "__main__":

    #############################################
    # SETUP - process user args, setup filenames
    #############################################

    # Check correct packages/programs installed
    check_program_exists(progName="dot2tex")
    check_module_exists(mod="pydot")
    check_module_exists(mod="pyparsing")

    # Get command line arguments, parse them
    args = get_parser().parse_args()

    # Store stem of input filename (i.e. without .xyz bit) for use
    # later for default PDF/GV etc filenames
    name = os.path.basename(args.input)  # just filename and extension
    stemName, extension = os.path.splitext(name)

    # Store filepath
    filePath = get_full_path(args.input)

    # Note that checking that the file exists is done in the individual parsers

    # Try and guess input type if not specified, based on file extension.
    # (could be done more sophisticatedly, I guess)
    # NO checking done if user option =/= actual file type!
    if not args.inputType:
        if extension == ".hepmc":
            args.inputType = "HEPMC"
        else:
            args.inputType = "PYTHIA"
        print "Assuming input type", args.inputType

    # Set default mode based on input type (only temporary)
    # TODO: remove me
    if not args.mode:
        if args.inputType == "HEPMC":
            args.mode = "EDGE"
        else:
            args.mode = "NODE"

    # Store output GraphViz filename
    # Default filename for output GraphViz file based on inputFilename
    # if user doesn't specify one
    gvFilename = args.outputGV
    if not gvFilename:
        gvFilename = stemName+".gv"
        gvFilename = os.path.join(filePath, gvFilename)

    # Filename for output PDF
    # Default filename for output PDF based on inputFilename
    # if user doesn't specify one
    pdfFilename = args.outputPDF
    if not pdfFilename:
        pdfFilename = stemName+"_"+args.mode+".pdf"
        pdfFilename = os.path.join(filePath, pdfFilename)

    # For debugging - print output & various debug messages to screen
    CONFIG.VERBOSE = args.verbose

    ###########################################
    # MAIN - Start of file processing routines
    ###########################################

    #-----------------------------------------------------------------------
    # Parse input file, depending on file contents (HepMC or Pythia8 output)
    #-----------------------------------------------------------------------
    event = None  # Hold GenEvent as result fo file parsing

    if args.inputType == "PYTHIA":
        print "Ignoring --eventNumber option as not relevant"
        event = pythiaParser.parse(filename=args.input)
        if CONFIG.removeRedundants:
            event.removeRedundantNodes()

    elif args.inputType == "HEPMC":
        event = hepmcParser.parse(filename=args.input,
                                  eventNumber=args.eventNumber)
        # Post processing - don't like this being here, move it!
        event.addVerticesForFinalState()  # TODO: fixme, sets all final?
        event.markInitialHepMC()
        event.removeRedundantEdges()
        if CONFIG.removeRedundants:
            event.removeRedundantsEdges()

    #-----------------------------------------------------------------------
    # Write relationships to GraphViz file, with Particles as Edges or Nodes
    #-----------------------------------------------------------------------
    if args.mode == "NODE":
        nodeWriter.printNodeToGraphViz(event, gvFilename=gvFilename,
                                       useRawNames=args.rawNames)
    else:
        if args.inputType == "PYTHIA":
            raise Exception("Can't do that at the moment, try NODE mode")
        edgeWriter.printEdgeToGraphViz(event, gvFilename=gvFilename,
                                       useRawNames=args.rawNames)

    #-----------------------------------------------------------------------
    # Run pdflatex or dot to produce the PDF
    #-----------------------------------------------------------------------
    if args.noPDF:
        print ""
        print "Not converting to PDF"
        print "If you want a PDF, run without --noPDF"
        print "and if you only want the raw names (faster to produce),"
        print "then run with --rawNames"
        print ""
    else:
        pdfPrinter.print_pdf(args, stemName, gvFilename, pdfFilename)
