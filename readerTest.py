#!/usr/bin/env python

"""
Tester for routines in hepmcReader.py
"""

import hepmcReader as h
import config


config.VERBOSE = True
# h.parse()
h.parse("5evt_HLT.hepmc")