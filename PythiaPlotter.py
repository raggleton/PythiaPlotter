"""
Main script to run PythiaPlotter.
"""

import user_args


class PythiaPlotter():
    """
    Store central objects & args used
    """
    def __init__(self, opts):
        self.opts = opts
        self.parser = None
        self.printer = None
        self.gen_event = None

        # Choose parser
        if opts.inputFormat == "PYTHIA":
            self.parser = PythiaParser(opts.input, opts.eventNumber)
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

    def parse_event(self, thingtoparse, event_num):
        # return self.parser.parse(thingtoparse)
        pass

    def print_event(self, gen_event):
        # self.printer.print_event(gen_event)
        pass


def main():
    # Central Pythia_Plotter object to keep track of the parser, printer, etc
    pp = PythiaPlotter(user_args.get_args())

    # for event in event_list:
    thingtoparse = None
    gen_event = pp.parse_event(thingtoparse)
    pp.print_event(gen_event)


if __name__ == "__main__":
    main()