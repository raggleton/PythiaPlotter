"""
Main script to run PythiaPlotter.
"""

import sys
import utils.user_args as user_args
import parsers
import printers
import networkx as nx


class PythiaPlotter(object):
    """
    Central object to keep track of the parser, printer, etc
    """

    def __init__(self, opts):
        self.opts = opts
        self.parser = None
        self.printer = None
        self.event = None

        # Choose parser
        if opts.inputFormat == "PYTHIA":
            self.parser = parsers.PythiaParser(opts.input)
        elif opts.inputFormat == "HEPMC":
            pass

        # Choose printer
        if opts.render == "DOT":
            pass
        elif opts.render == "LATEX":
            pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def parse_print(self):
        """Do parsing and printing in one call."""
        self.parse_event()
        self.print_event()

    def parse_event(self):
        self.event = self.parser.parse()

    def print_event(self):
        pass


def main(args):
    pp = PythiaPlotter(user_args.get_args(args))
    pp.parse_print()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))