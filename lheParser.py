"""
Parser for LHE files.

Return GenEvent with GenParticles.
"""

import xml.etree.ElementTree as ET


def parseLHE(filename, eventNumber=0):
    """Reads in LHE file and returns GenEvent"""
    # TODO: what if no filename? or bad?
    tree = ET.parse(filename)
    root = tree.getroot()
    events = root.findall('event')
    # use splitlines to do \n correctly, and if l.strip() to remove blank lines
    raw_event = [l for l in events[eventNumber].text.splitlines() if l.strip()]
    for l in raw_event:
        print l
