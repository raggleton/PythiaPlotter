#!/usr/bin/env python

"""
Tester for routines in hepmcParser.py
"""

import hepmcParser as h
import pythiaParser as p
import config


CONFIG.VERBOSE = False
# eventList = h.parse()
# eventList = h.parse("test/testSamples/testSimple.hepmc")
eventList = h.parse("test/testSamples/test_3to1to2.hepmc")
# eventList = h.parse("5evt_HLT.hepmc")
# e = p.parse("test/testSamples/testEvent.txt")
# print "Parsed",len(eventList),"events"
# e.markInteresting(CONFIG.interesting)

# for p in e.particles:
#     from pprint import pprint
#     pprint(vars(p))
#
# print e.getInitialParticles()