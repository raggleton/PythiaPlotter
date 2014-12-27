"""
Parser for LHE files.

Return GenEvent with GenParticles.
"""

import xml.etree.ElementTree as ET

# PythiaPlotter imports
from eventClasses import *


def parseLHE(filename, eventNumber=0):
    """Reads in LHE file and returns GenEvent with GenParticles."""
    # TODO: what if no filename? or bad?
    tree = ET.parse(filename)
    root = tree.getroot()
    
    # Get setup info (beam info, etc)
    init = root.findall('init')
    if len(init) != 1:
        raise Exception("No <init> block, or more than 1!")
    currentEvent = parseInitialBlock(init[0].text)
    
    # Get chosen event info
    events = root.findall('event')    
    parseEventBlock(events[eventNumber].text, currentEvent)


def isCommentLine(line):
    """Test if line is comment."""
    commentLine = ["#", "<--"]  # List of strings that indicate a comment
    for c in commentLine:
        if line.strip().startswith(c):
            return True
    else:
        return false

# TODO: generator method to loop through lines of blocks?

def parseInitialBlock(block):
    """Parses LHE initial block and returns GenEvent."""
    
    firstLine = True
    # use splitlines to do \n correctly, and if l.strip() to remove blank lines
    for line in [l for l in block.splitlines() if l.strip()]:
        if not isCommentLine(line):
            if firstLine:
                parseCommonInitialInfo(line)
                firstLine = False
            else:
                parseProcessLine(line, currentEvent)

    return currentEvent

def parseCommonInitialInfo(line):
    """Parse LHE intial block first line.

    Format: <beam1 PDGID> <beam2 PDGID> <beam1 energy> <beam2 energy> 
    <beam1 pdfset> <beam2 pdfset> <beam1 pdf?> <beam2 pdf?> 
    <weighting strategy> <# processes> (all on one line)
    """
    pass


def parseProcessLine(line, currentEvent):
    """Parse LHE process information line in <intial> block.
    
    Format (for each process):
    <XSECUP> <XERRUP> <XMAXUP> <process label> (one line)
    """
    pass


def parseEventBlock(block, currentEvent):
    """Parses LHE event block and returns list of GenParticles???"""
    firstLine = True
    counter = 1
    # particles = []
    # use splitlines to do \n correctly, and if l.strip() to remove blank lines
    for line in [l for l in block.splitlines() if l.strip()]:
        if not isCommentLine(line):
            if firstLine:
                parseCommonEventInfo(line)
                firstLine = False
            else:
                currentEvent.particles.append(parseParticleLine(line, counter))
                counter += 1

    # return particles

def parseCommonEventInfo(line, currentEvent):
    """Parses the one line with common event info immediately after <event>.
    Requires GenEvent object to add info to. 
    # TODO: test if None and create one instead?
    
    Format: <# particles in event> <process ID number> <event weight> 
    <scale> <alpha_QED> <alpha_QCD>
    (all on one line)
    """

    parts = line.strip().split()
    currentEvent.scale = parts[3]
    currentEvent.alphaQCD = parts[5]
    currentEvent.alphaQED = parts[4]
    currentEvent.signalProcessID = parts[1]


def parseParticleLine(line, barcode):
    """Parses a line with information about a particle in an event.

    Format: <PDGID> <status> <mother1> <mother2> <colour1> <colour2> <p_x> 
    <p_y> <p_z> <energy> <mass> <proper lifetime> <spin>
    (all on one line)

    The mother numbers refers to their position in the event listing 
    (particles go from 1..). This is passe din as argument "barcode"
    """

    parts = line.strip().split()
    p = GenParticle(barcode=str(barcode), pdgid=parts[0], 
                    px=parts[6], py=parts[7], pz=parts[8], energy=parts[9],
                    mass=parts[10], status=parts[1])

    mother1 = int(parts[2])
    mother2 = int(parts[3])

    # TODO: status - initial.final state?
    
    # TODO: check if mother1 = mother2, or one = 0?

    p.node_attr.mother1 = mother1
    p.node_attr.mother2 = mother2

    return p