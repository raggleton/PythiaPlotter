"""Printers take in a NetworkX graph of Particles, then produce an output diagram.

Attributes
----------

printer_opts_all : dict[str, PrinterOption]
    Store a record of all printers and their requirements.

printer_opts_checked : dict{str: PrinterOption}
    Store a record of only those printers available on the user's system.
"""


from __future__ import absolute_import
import sys
from pythiaplotter.utils.common import check_program_exists, check_module_exists, generate_repr_str
from .dot_printer import DotPrinter
from .web_printer import VisPrinter


class PrinterOption(object):

    def __init__(self, description, printer, requires, default_output_fmt):
        """Basic class to hold info about an output printer.

        Parameters
        ----------
        description : str
            Short description about this printer
        printer : class
            Printer class
        requires : dict
            Dict of program and module lists that are needed for this printer
        default_output_fmt : str
            Default output file extension
        """
        self.description = description
        self.printer = printer
        self.requires = requires
        self.default_output_fmt = default_output_fmt

    def __repr__(self):
        return generate_repr_str(self)

    def __str__(self):
        return self.description


# List of all possible printers and their requirements
printer_opts_all = {
    "DOT": PrinterOption(
        description="Fast, but basic formatting",
        printer=DotPrinter,
        requires={
            "programs": ["dot"]  # assuming that sfdp, neato etc also work...
        },
        default_output_fmt="pdf"
    ),
    "WEB": PrinterOption(
        description="Interactive diagram in your browser",
        printer=VisPrinter,
        requires={
            "programs": ["dot"]
        },
        default_output_fmt="html"
    ),
    # "LATEX": PrinterOption(
    #     description="Slower, but fancier formatting",
    #     printer=None,
    #     requires={
    #         "programs": ['something here'],
    #         "modules": ['py2tex']
    #     }
    # )
}


# Create a similar dict, but only if each printer has
# the necessary programs and py modules available
printer_opts_checked = {}

for pname, popt in printer_opts_all.items():
    required_progs = popt.requires.get('programs', [])
    required_mods = popt.requires.get('modules', [])

    if (all(check_program_exists(prog) for prog in required_progs)
        and all(check_module_exists(mod) for mod in required_mods)):
        printer_opts_checked[pname] = popt


def print_printers_requirements(output=sys.stdout.write):
    """Print program and python package requirements for all printers

    Parameters
    ----------
    output : function, optional
        The outputmessage is passed as the parameter to this function.
        Default is sys.stdout.write()
    """
    require_str = ["Requirements for each printing option:\n"]
    for pname, popt in printer_opts_all.items():
        require_str.append('{0}:'.format(pname))
        require_str.append('\tPrograms: {0}'.format(popt.requires.get('programs', None)))
        require_str.append('\tPython packages: {0}'.format(popt.requires.get('module', None)))
        require_str.append('\n')
    output("\n".join(require_str))
