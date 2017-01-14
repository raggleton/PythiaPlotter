"""
To handle input args & subsequent modifications
"""


import pythiaplotter.utils.logging_config  # NOQA
import logging
import argparse
import os.path
import pythiaplotter.utils.common as helpr
from pythiaplotter.parsers import parser_opts
from pythiaplotter.printers import printer_opts_checked, printer_opts_all


log = logging.getLogger(__name__)


def get_args(input_args):
    """Get argparse.Namespace of parsed user arguments, with sensible defaults set."""

    parser = argparse.ArgumentParser(
        prog="PythiaPlotter",
        description="Convert MC event into a particle evolution diagram.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    #################
    # Input options
    #################
    input_group = parser.add_argument_group('Input Options')

    input_group.add_argument("input",
                             help="Input file")

    parser_help = ["Input formats:"]
    for k, v in parser_opts.iteritems():
        help_str = "{0}: {1}".format(k, v.description)
        if v.file_extension:
            help_str += " (default for files ending in {})".format(v.file_extension)
        parser_help.append(help_str)

    input_group.add_argument("--inputFormat",
                             help="\n".join(parser_help),
                             choices=parser_opts.keys())
    input_group.add_argument("-n", "--eventNumber",
                             help="Select event number to plot, starts at 1.\n"
                                  "For: HEPMC, LHE input formats.\n",
                             type=int,
                             default=0)

    #################
    # Output file options
    #################
    output_group = parser.add_argument_group('Output Options')

    output_group.add_argument("-O", "--outputPDF",
                              help="Output PDF filename "
                                   "(if unspecified, defaults to INPUT.pdf)")
    output_group.add_argument("--openPDF",
                              help="Automatically open PDF once plotted",
                              action="store_true")

    #################
    # Render options
    #################
    output_group.add_argument("--noPDF",
                              help="Don't convert Graphviz file to PDF",
                              action="store_true")

    # TODO: unify "printer" vs "renderer"
    # TODO: printout usual help then this, not just this error message
    if len(printer_opts_checked.keys()) == 0:
        require_error_str = ["ERROR: None of the required programs or python modules "
                             "for any rendering option exist.",
                             "Requirements for each printing option:"]
        for pname, popt in printer_opts_all.iteritems():
            require_error_str.append('{0}:'.format(pname))
            require_error_str.append('\tPrograms: {0}'.format(popt.requires.get('programs', None)))
            # TODO: really these are packages...
            require_error_str.append('\tPython modules: {0}'.format(popt.requires.get('module', None)))
            require_error_str.append('\n')
        print "\n".join(require_error_str)
        exit(1)

    render_help = ["Render method:"]
    render_help.extend(["{0}: {1}".format(k, v.description)
                        for k, v in printer_opts_checked.iteritems()])
    output_group.add_argument("-r", "--render",
                              help="\n".join(render_help),
                              choices=printer_opts_checked.keys(),
                              default="DOT" if "DOT" in printer_opts_checked else "LATEX")

    output_group.add_argument("--redundants",
                              help="Keep redundant particles (defualt is to remove them)",
                              action="store_true")

    #################
    # Miscellaneous options
    #################
    misc_group = parser.add_argument_group("Miscellaneous Options")

    misc_group.add_argument("-v", "--verbose",
                            help="Print debug statements to screen",
                            action="store_true")
    misc_group.add_argument("--stats",
                            help="Print some statistics about the event/graph",
                            action="store_true")

    args = parser.parse_args(input_args)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    args.input = helpr.cleanup_filepath(args.input)  # sanitise input

    if not helpr.check_file_exists(args.input):
        raise IOError("No such file: '%s'" % args.input)

    # Post process user args
    set_default_output(args)
    set_default_format(args)
    set_default_mode(args)

    for k, v in args.__dict__.iteritems():
        log.debug("{0}: {1}".format(k, v))

    return args


def set_default_output(args):
    """Set default output filenames and stems/dirs"""
    args.stem_name, args.extension = os.path.splitext(os.path.basename(args.input))
    args.input_dir = helpr.get_full_path(args.input)

    # Set default PDF filename if not already done
    if not args.outputPDF:
        filename = args.stem_name + "_" + str(args.eventNumber) + ".pdf"
        args.outputPDF = os.path.join(args.input_dir, filename)

    # Set default graphviz filename from PDF name
    # TODO: too tightly coupled to dot printer - make more generic!
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
    """Set default particle mode (representation) if the user hasn't."""
    args.particleMode = parser_opts[args.inputFormat].default_representation
    log.info("Using %s particle representation" % args.particleMode)


def print_options(args):
    """Printout for user arguments."""
    for k, v in args.__dict__.iteritems():
        print "{0}: {1}".format(k, v)
