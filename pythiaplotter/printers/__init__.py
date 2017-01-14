from dot_printer import DotPrinter
from pythiaplotter.utils.common import check_program_exists, check_module_exists


"""
Store a record of both all designed printers, as well as only those available on the user's system,
along with their metainfo.
"""


class PrinterOption(object):

    def __init__(self, description, printer, requires):
        """Basic class to hold info about an output printer.

        description : str
            Short description about this printer

        printer :
            Printer class

        requires : dict
            Dict of program and module lists that are needed for this printer
        """
        self.description = description
        self.printer = printer
        self.requires = requires

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description


# List of all possible printers and their requirements
printer_opts_all = {
    "DOT": PrinterOption(
        description="Fast, but basic formatting",
        printer=DotPrinter,
        requires={
            "programs": ["dot"]
        }
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
for pname, popt in printer_opts_all.iteritems():
    required_progs = popt.requires.get('programs', [])
    required_mods = popt.requires.get('modules', [])

    if (all(check_program_exists(prog) for prog in required_progs)
        and all(check_module_exists(mod) for mod in required_mods)):
        printer_opts_checked[pname] = popt
