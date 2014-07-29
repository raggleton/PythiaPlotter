#!/usr/bin/env python

"""
Tester for routines in hepmcParser.py
"""

import hepmcParser as h
import config


config.VERBOSE = False
# eventList = h.parse()
eventList = h.parse("test/testSimple.hepmc")
# eventList = h.parse("5evt_HLT.hepmc")
print "Parsed",len(eventList),"events"