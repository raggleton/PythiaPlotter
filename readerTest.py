#!/usr/bin/env python

"""
Tester for routines in hepmcParser.py
"""

import hepmcParser as h
import pythiaParser as p
import config


config.VERBOSE = True
# eventList = h.parse()
# eventList = h.parse("test/testSimple.hepmc")
# eventList = h.parse("5evt_HLT.hepmc")
e = p.parse("test/testEvent.txt")
# print "Parsed",len(eventList),"events"
e.markInteresting(config.interesting)

for p in e.particles:
    from pprint import pprint
    pprint(vars(p))