"""
To handle input args & subsequent modifications
"""


import logging_config
import logging
import argparse
import os.path
import pythiaplotter.utils.common as helpr
import pythiaplotter.utils.requisite_checker as checkr
from pythiaplotter.parsers import parser_opts


log = logging.getLogger(__name__)


def get_args(input_args):
    """Define all command-line options. Returns ArgumentParser object."""

    parser = argparse.ArgumentParser(
        description="Convert MC event into particle evolution diagram.\n"
                    "Uses dot/Graphviz/dot2tex/pdflatex to make a PDF.",
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter
        formatter_class=argparse.RawTextHelpFormatter
    )

    #################
    # Input options
    #################
    parser.add_argument("input",
                        help="Input file")

    parser_help = ["Input formats:"]
    for k, v in parser_opts.iteritems():
        help_str = "{0}: {1}".format(k, v.description)
        if v.file_extension:
            help_str += " (default for files ending in {})".format(v.file_extension)
        parser_help.append(help_str)

    parser.add_argument("--inputFormat",
                        help="\n".join(parser_help),
                        choices=parser_opts.keys())
    parser.add_argument("-n", "--eventNumber",
                        help="Select event number to plot, starts at 1.\n"
                             "For: HEPMC, LHE input formats.\n",
                        type=int, default=0)

    #################
    # Output file options
    #################
    # parser.add_argument("-oGV", "--outputGV",
    #                     help="output Graphviz filename "
    #                          "(if unspecified, defaults to INPUT.gv)")
    parser.add_argument("-O", "--outputPDF",
                        help="Output PDF filename "
                             "(if unspecified, defaults to INPUT.pdf)")
    parser.add_argument("--openPDF",
                        help="Automatically open PDF once plotted",
                        action="store_true")

    #################
    # Render options
    #################
    # parser.add_argument("-p", "--particleMode",
    #                     choices=["NODE", "EDGE"],
    #                     help="Particle representation (see README)")
    parser.add_argument("--noPDF",
                        help="Don't convert Graphviz file to PDF",
                        action="store_true")

    # Check to see if certain render modes are available.
    # If not, don't give them to the user as options
    render_opts = {"DOT": "Fast, but basic formatting"}
                   # "LATEX": "Slower, but nicer formatting"}

    latex_check = checkr.RequisiteChecker(modules=["pydot", "pyparsing"],
                                          programs=["dot2tex"])
    if not latex_check.all_exist():
        render_opts.pop("LATEX", None)

    dot_check = checkr.RequisiteChecker(programs=["dot"])
    if not dot_check.all_exist():
        render_opts.pop("DOT", None)

    if len(render_opts.keys()) == 0:
        raise EnvironmentError("You are mising programs. Cannot render.")

    render_help_str = "Render method:\n"
    for k, v in render_opts.items():
        render_help_str += k + ": " + v + "\n"

    parser.add_argument("-r", "--render",
                        help=render_help_str,
                        choices=render_opts,
                        default="DOT" if "DOT" in render_opts else "LATEX")

    parser.add_argument("--redundants",
                        help="Keep redundant particles (defualt is to remove them)",
                        action="store_true")

    #################
    # Testing options
    #################
    # parser.add_argument("--showVertexBarcode",  # think of a better opt name!
    #                     help="Show vertex barcodes, useful for figuring out "
    #                          "which are the hard interaction(s). Only useful "
    #                          "when in EDGE mode.",
    #                     action="store_true")
    # parser.add_argument("--hardVertices",
    #                     help='List of vertex barcode(s) that contain the '
    #                          'hard interaction, e.g. --hardVertices V2, V3 '
    #                          '(LATEX render only)',
    #                     default=None, nargs='*', type=str)
    # parser.add_argument("--scale",
    #                     help="Factor to scale PDF by (LATEX render only)",
    #                     default=0.7, type=float)
    parser.add_argument("-v", "--verbose",
                        help="Print debug statements to screen",
                        action="store_true")
    parser.add_argument("--stats",
                        help="Print some statistics about the event/graph",
                        action="store_true")

    #################
    # Post process user args
    #################
    args = parser.parse_args(input_args)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not helpr.check_file_exists(args.input):
        raise IOError("No such file: '%s'" % args.input)

    set_default_output(args)
    set_default_format(args)
    set_default_mode(args)
    if args.verbose:
        print_options(args)
    # log.debug("Args: %s" % args)

    return args


def set_default_output(args):
    """Set default output filenames and stems/dirs"""
    args.input = helpr.cleanup_filepath(args.input)  # sanitise input
    args.in_name = os.path.basename(args.input)  # just filename and extension
    args.stem_name, args.extension = os.path.splitext(args.in_name)
    args.in_dir = helpr.get_full_path(args.input)

    # Set default PDF filename if not already done
    if not args.outputPDF:
        filename = args.stem_name + "_" + str(args.eventNumber) + ".pdf"
        args.outputPDF = os.path.join(args.in_dir, filename)

    # Set default graphviz filename from PDF name
    args.outputGV = args.outputPDF.replace(".pdf", ".gv")


def set_default_format(args):
    """Set default input format if the user hasn't."""
    if not args.inputFormat:
        for pname, popt in parser_opts.iteritems():
            if args.extension.lower() == popt.file_extension:
                args.inputFormat = pname
                log.info("You didn't set an input format. Assuming %s" % args.inputFormat)
                break
        else:
            raise RuntimeError("Cannot determine input format. Please specify.")


def set_default_mode(args):
    """Set default particle mode if the user hasn't."""
    args.particleMode = None
    if not args.particleMode:
        if args.inputFormat == "HEPMC":
            args.particleMode = "EDGE"
        else:
            args.particleMode = "NODE"
        log.info("You didn't set a particle mode. Using %s" % args.particleMode)


def print_options(args):
    """Printout for user arguments."""
    for k, v in args.__dict__.iteritems():
        print "{0}: {1}".format(k, v)
