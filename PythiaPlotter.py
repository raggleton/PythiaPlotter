"""
Main script to run PythiaPlotter.
"""

import helper_methods as helper
from Requisite_Checker import Requisite_Checker


class Pythia_Plotter():
    """
    Store central objects & args used
    """
    def __init__(self):
        self.parser = None
        self.printer = None
        self.gen_event = None

    def parse_event(self, event):
        # return self.parser.parse(event)
        pass

    def print_event(self, gen_event):
        # self.printer.print_event(gen_event)
        pass


if __name__ == "__main__":

    # Check for optional modules & programs to determine what we can do
    checkr = Requisite_Checker(modules=["pydot", "pyparsing"],
                               programs=["dot2tex"])

    # Central Pythia_Plotter object to keep track of the parser, printer, etc
    pp = Pythia_Plotter()

    # for event in event_list:
    gen_event = pp.parse_event(event)
    pp.print_event(gen_event)