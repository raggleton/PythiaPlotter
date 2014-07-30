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
p.parse()
# print "Parsed",len(eventList),"events"