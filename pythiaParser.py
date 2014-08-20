"""
For parsing the output of PYTHIA8 that it prints to screen.

"""
from pprint import pprint
import re

# PythiaPlotter files
from eventClasses import *
import config as CONFIG


def parse(filename="qcdScatterSmall.txt"):
    """Parse PYTHIA8 screen output and return event full of NodeParticles"""

    currentEvent = GenEvent()

    # List of Particle objects in full event,
    # in order of number in event listing.
    # So the object at fullEvent[i] has self.barcode = i
    # Can then add to GenEvent at the end
    particleList = []

    # Open input file & parse event info
    with open(filename, "r") as inputFile:

        print "Reading event listing from %s" % filename

        # For processing the full output from Pythia, triggers where blocks
        # of info start/stop. Use `if <trigger> in line:`
        infoStart = "-  PYTHIA Info Listing"
        infoEnd = "End PYTHIA Info Listing"

        fullEventStart = "-  PYTHIA Event Listing  (complete event)"
        fullEventEnd = "End PYTHIA Event Listing"

        hardEventStart = "-  PYTHIA Event Listing  (hard process)"
        hardEventEnd = "End PYTHIA Event Listing"

        statsStart = "-  PYTHIA Event and Cross Section Statistics"
        statsEnd = "End PYTHIA Event and Cross Section Statistics"

        # To hold list of lines for parsing in separate methods
        addToBlock = False
        block = []

        # Read in file to list of Particles
        for line in inputFile:

            if addToBlock:
                block.append(line)

            # Go through file, looking for matches to triggers
            # Must be a more succint way to do this
            # Look for event info listing
            if infoStart in line:
                addToBlock = True
                if CONFIG.VERBOSE: print "Event Info start"

            elif addToBlock and infoEnd in line:
                addToBlock = False
                currentEvent = parseInfo(block)
                if CONFIG.VERBOSE: print "Event Info end"
                if CONFIG.VERBOSE: pprint(block)
                if CONFIG.VERBOSE: print len(block)
                del block[:]  # empty list of lines

            # Look for cross-section & events stats
            elif statsStart in line:
                addToBlock = True
                if CONFIG.VERBOSE: print "Event Stats Start"

            elif addToBlock and statsEnd in line:
                addToBlock = False
                # parseStats(block)
                if CONFIG.VERBOSE: print "Event Stats End"
                if CONFIG.VERBOSE: pprint(block)
                if CONFIG.VERBOSE: print len(block)
                del block[:]

            # Look for event particle listing
            elif fullEventStart in line:
                addToBlock = True
                if CONFIG.VERBOSE: print "Event Listing Starts"

            elif addToBlock and fullEventEnd in line:
                addToBlock = False
                currentEvent.particles = parseEventListing(block)
                if CONFIG.VERBOSE: print "Event Listing Ends"
                if CONFIG.VERBOSE: print len(block)
                del block[:]

        print "Done reading file"

    # Once got all particles, add mothers/daughters
    if CONFIG.VERBOSE: print "Adding mothers"
    currentEvent.addNodeMothers()
    if CONFIG.VERBOSE: print "Adding daughters"
    currentEvent.addNodeDaughters()

    # Convert Node to Edge repr for all particles so we can plot either later
    # [p.convertNodeToEdgeAttributes(currentEvent)
    # for p in currentEvent.particles]
    # currentEvent.convertNodesToEdges()
    # currentEvent.markInitialHepMC()

    # Things like mark interesting, remove redundants done in main script, as
    # required for both HepMC and Pythia
    return currentEvent


def parseInfo(block):
    """Parse Event Info listing block, return """
    currentEvent = GenEvent()
    currentPdf = PdfInfo()

    # CHECK UNITS
    # Must be a better way than this?
    for line in block:
        line = line.strip()
        line = re.sub(",", "", line)  # Remove comma separation
        parts = line.split()
        if line.startswith("Beam A") or line.startswith("Beam B"):
            pass  # Info about incoming protons
        elif line.startswith("In 1"):  # Parton 1 info
            currentPdf.id1 = parts[4]
            currentPdf.x1 = parts[7]
            currentPdf.pdf1 = parts[10]
            currentPdf.scalePDF = parts[-1].strip(".")
        elif line.startswith("In 2"):  # Parton 2 info
            currentPdf.id2 = parts[4]
            currentPdf.x2 = parts[7]
            currentPdf.pdf2 = parts[10]
        elif line.startswith("Subprocess"):
            m = re.search('code ([0-9]*)', line)  # Gets signal process ID
            currentEvent.signalProcessID = m.group(1)
        elif line.startswith("It has"):
            pass
        elif line.startswith("alphaEM"):
            currentEvent.alphaEM = parts[2]
            currentEvent.alphaQCD = parts[5]
            currentEvent.scale = parts[-1].strip(".")
        elif line.startswith("Impact"):
            pass  # Info about impact param
        elif line.startswith("Max"):
            pass  # Info about Max pT scale for MPI
        elif line.startswith("Number of MPI"):
            currentEvent.numMPI = parts[4]

    currentEvent.pdf_info = currentPdf
    return currentEvent


def parseStats(block):
    """Parse cross section information, and return object"""
    pass


def parseEventListing(block):
    """Parse full event particle listing, returns list of GenParticles"""

    # Where particle listing starts and stops
    listingStart = """no        id"""
    listingEnd = """Charge sum"""

    particleList = []

    parseLine = False
    for line in block:
        line = line.strip()
        if line.startswith(listingStart):
            parseLine = True
            continue
        elif line.startswith(listingEnd):
            parseLine = False
            continue

        if "system" in line:
            continue

        if parseLine:
            # print line
            particleList.append(parseParticleLine(line))

    # Note, adding of daughters/mothers done in main parse() method
    return particleList


def parseParticleLine(line):
    """Parse line with particle info, and return GenParticle object
    with NodeAttributes set"""

    # if CONFIG.VERBOSE: print line,

    parts = line.split()
    # name = parts[2]
    # d1 = int(parts[6])
    # d2 = int(parts[7])
    flowDict = {}
    if int(parts[8]) or int(parts[9]):
        flowDict[1] = int(parts[8])
        flowDict[2] = int(parts[9])

    p = GenParticle(barcode=parts[0],
                    pdgid=parts[1],
                    status=parts[3],
                    px=parts[10],
                    py=parts[11],
                    pz=parts[12],
                    energy=parts[13],
                    mass=parts[14],
                    flowDict=flowDict)

    mother1 = int(parts[4])
    mother2 = int(parts[5])

    # Following only true if reading from Pythia screen output.
    # HepMC uses different codes.
    if p.status > 0:
        p.isFinalState = True

    if (mother1 == 0 and mother2 == 0):
        p.isInitialState = True

    # Sometimes Pythia sets m2 == 0 if only 1 mother & particle from shower
    # This causes looping issues, so set m2 = m1 if that's the case
    if (mother1 and not mother2):
        mother2 = mother1

    p.node_attr.mother1 = mother1
    p.node_attr.mother2 = mother2

    return p
