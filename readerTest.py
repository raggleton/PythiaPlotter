#!/usr/bin/env python

"""
Tester for routines in hepmcReader.py
"""

import hepmcReader as h
import config


config.VERBOSE = False
# eventList = h.parse()
eventList = h.parse("testing/testSimple.hepmc")
# eventList = h.parse("5evt_HLT.hepmc")
print "Parsed",len(eventList),"events"