#!/usr/bin/env python

"""
Main script to run PythiaPlotter.
"""

import logging
import pythiaplotter.utils.logging_config  # NOQA
import sys

import pythiaplotter.parsers as parsers
import pythiaplotter.printers as printers
import pythiaplotter.cli as cli
from pythiaplotter.utils.common import open_pdf


log = logging.getLogger(__name__)


class PythiaPlotter(object):
    """Central object to keep track of the parser, printer, etc"""

    def __init__(self, opts):
        self.opts = opts
        self.parser = None
        self.printer = None
        self.event = None

        remove_redundants = not opts.redundants
        # Choose parser & configure
        if opts.inputFormat == "PYTHIA":
            self.parser = parsers.Pythia8Parser(filename=opts.input,
                                                event_num=opts.eventNumber,
                                                remove_redundants=remove_redundants)
        elif opts.inputFormat == "HEPMC":
            # For now, disable remove_redundants for HepMC until it gets fixed
            log.warning("Disabling removal of redundants for HepMC files as broken")
            self.parser = parsers.HepMCParser(filename=opts.input,
                                              event_num=opts.eventNumber,
                                              # remove_redundants=remove_redundants)
                                              remove_redundants=False)
        elif opts.inputFormat == "LHE":
            self.parser = parsers.LHEParser(filename=opts.input,
                                            event_num=opts.eventNumber,
                                            remove_redundants=remove_redundants)
        elif opts.inputFormat == "CMSSW":
            self.parser = parsers.CMSSWParticleListParser(filename=opts.input,
                                                          remove_redundants=remove_redundants)

        # Choose printer & configure
        if opts.render == "DOT":
            self.printer = printers.DotPrinter(gv_filename=opts.outputGV,
                                               pdf_filename=opts.outputPDF,
                                               renderer="dot",
                                               output_format="pdf")
        elif opts.render == "LATEX":
            pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def parse_event(self):
        """Run the object's parser"""
        self.event = self.parser.parse()
        if self.opts.stats:
            self.event.print_stats()

    def print_event(self):
        """Run the object's printer"""
        self.printer.print_event(self.event, pdf=(not self.opts.noPDF))
        if self.opts.openPDF:
            open_pdf(self.opts.outputPDF)


def main(args=sys.argv[1:]):
    pp = PythiaPlotter(cli.get_args(args))
    pp.parse_event()
    pp.event.label = "Alex's event in MG5_aMC@NLO"
    pp.event.event_num = pp.opts.eventNumber
    # pp.event.lumi_section = 123456798
    pp.print_event()


if __name__ == "__main__":
    sys.exit(main())
