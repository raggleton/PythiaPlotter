#!/usr/bin/env python

"""
Main script to run PythiaPlotter.
"""


from __future__ import absolute_import
import sys
import logging
import pythiaplotter.utils.logging_config  # NOQA

import pythiaplotter.parsers as parsers
import pythiaplotter.printers as printers
import pythiaplotter.cli as cli
from pythiaplotter.utils.common import open_pdf


log = logging.getLogger(__name__)


def choose_parser(opts):
    """Choose parser & configure"""

    remove_redundants = not opts.redundants

    if opts.inputFormat == "PYTHIA":
        return parsers.Pythia8Parser(filename=opts.input,
                                     event_num=opts.eventNumber,
                                     remove_redundants=remove_redundants)
    elif opts.inputFormat == "HEPMC":
        log.warning("Disabling removal of redundants for HepMC files as broken")
        return parsers.HepMCParser(filename=opts.input,
                                   event_num=opts.eventNumber,
                                   remove_redundants=remove_redundants)
    elif opts.inputFormat == "LHE":
        return parsers.LHEParser(filename=opts.input,
                                 event_num=opts.eventNumber,
                                 remove_redundants=remove_redundants)
    elif opts.inputFormat == "CMSSW":
        return parsers.CMSSWParticleListParser(filename=opts.input,
                                               remove_redundants=remove_redundants)
    elif opts.inputFormat == "HEPPY":
        return parsers.HeppyParser(filename=opts.input,
                                   event_num=opts.eventNumber,
                                   remove_redundants=remove_redundants)
    else:
        return None


def choose_printer(opts):
    """Choose printer & configure"""

    if opts.printer == "DOT":
        return printers.DotPrinter(output_filename=opts.output,
                                   renderer="dot",
                                   output_format=opts.outputFormat)
    elif opts.printer == "LATEX":
        return None


def main(in_args=None):
    opts = cli.get_args(in_args)
    parser = choose_parser(opts)
    event = parser.parse()
    if opts.stats:
        event.print_stats()
    event.label = "Alex's event in MG5_aMC@NLO"
    event.event_num = opts.eventNumber
    # pp.event.lumi_section = 123456798
    printer = choose_printer(opts)
    printer.print_event(event, make_diagram=(not opts.noOutput))
    if opts.open and not opts.noOutput:
        open_pdf(opts.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
