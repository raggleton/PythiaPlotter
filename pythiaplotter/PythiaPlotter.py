#!/usr/bin/env python

"""Main script to run PythiaPlotter."""


from __future__ import absolute_import
import sys
from pythiaplotter.utils.logging_config import get_logger

import pythiaplotter.parsers as parsers
import pythiaplotter.printers as printers
from pythiaplotter.graphers import assign_particles_to_graph
import pythiaplotter.cli as cli
from pythiaplotter.utils.common import open_pdf


log = get_logger(__name__)


def choose_parser(opts):
    """Choose parser & configure"""

    if opts.inputFormat == "PYTHIA":
        return parsers.Pythia8Parser(filename=opts.input,
                                     event_num=opts.eventNumber)
    elif opts.inputFormat == "HEPMC":
        return parsers.HepMCParser(filename=opts.input,
                                   event_num=opts.eventNumber)
    elif opts.inputFormat == "LHE":
        return parsers.LHEParser(filename=opts.input,
                                 event_num=opts.eventNumber)
    elif opts.inputFormat == "CMSSW":
        return parsers.CMSSWParticleListParser(filename=opts.input)
    elif opts.inputFormat == "HEPPY":
        return parsers.HeppyParser(filename=opts.input,
                                   event_num=opts.eventNumber)
    else:
        raise NotImplementedError("Cannot parse input format %s" % opts.inputFormat)


def main(in_args=None):
    """Main entry point to run the whole thing."""
    opts = cli.get_args(in_args)
    parser = choose_parser(opts)
    event, particles = parser.parse()
    default_repr = parsers.parser_opts[opts.inputFormat].default_representation
    graph = assign_particles_to_graph(particles, default_repr,
                                      desired_repr=opts.representation,
                                      remove_redundants=(not opts.redundants))
    event.graph = graph
    if opts.stats:
        event.print_stats()
    printer = printers.printer_opts_checked[opts.printer].printer(opts)
    printer.print_event(event)
    if opts.open and not opts.noOutput:
        open_pdf(opts.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
