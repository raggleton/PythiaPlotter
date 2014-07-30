"""
For parsing the output of PYTHIA8 that it prints to screen.

"""
from pprint import pprint
import re

# PythiaPlotter files
from eventClasses import *
import config  # For my Global definitions


def parse(filename="qcdScatterSmall.txt"):
    """Parse PYTHIA8 screen output and return event full of NodeParticles"""

    currentEvent = GenEvent()

    # List of Particle objects in full event,
    # in order of number in event listing.
    # So the object at fullEvent[i] has self.barcode = i
    # Can then add to GenEvent at the end
    fullEvent = []

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
                if config.VERBOSE: print "Event Info start"

            elif addToBlock and infoEnd in line:
                addToBlock = False
                parseInfo(block)
                if config.VERBOSE: print "Event Info end"
                if config.VERBOSE: pprint(block)
                if config.VERBOSE: print len(block)
                del block[:]  # empty list of lines

            # Look for cross-section & events stats
            elif statsStart in line:
                addToBlock = True
                if config.VERBOSE: print "Event Stats Start"

            elif addToBlock and statsEnd in line:
                addToBlock = False
                parseStats(block)
                if config.VERBOSE: print "Event Stats End"
                if config.VERBOSE: pprint(block)
                if config.VERBOSE: print len(block)
                del block[:]

            # Look for event particle listing
            elif fullEventStart in line:
                addToBlock = True
                if config.VERBOSE: print "Event Listing Starts"

            elif addToBlock and fullEventEnd in line:
                addToBlock = False
                # currentEvent.particles = parseEventListing(block)
                if config.VERBOSE: print "Event Listing Ends"
                if config.VERBOSE: print len(block)
                del block[:]

        line = ""
        print "Done reading file"

    # markInteresting(fullEvent=fullEvent, interestingList=config.interesting)

    # addMothers(fullEvent=fullEvent)

    # addDaughters(fullEvent=fullEvent)

    # if config.removeRedundants:
    #     removeRedundants(fullEvent=fullEvent)

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
            currentPdf.id1 = int(parts[4])
            currentPdf.x1 = float(parts[7])
            currentPdf.pdf1 = float(parts[10])
            currentPdf.scalePDF = float(parts[-1].strip("."))
        elif line.startswith("In 2"):  # Parton 2 info
            currentPdf.id2 = int(parts[4])
            currentPdf.x2 = float(parts[7])
            currentPdf.pdf2 = float(parts[10])
        elif line.startswith("Subprocess"):
            m = re.search('code ([0-9]*)', line)  # Gets signal process ID
            currentEvent.signalProcessID = int(m.group(1))
        elif line.startswith("It has"):
            pass
        elif line.startswith("alphaEM"):
            currentEvent.alphaEM = float(parts[2])
            currentEvent.alphaQCD = float(parts[5])
            currentEvent.scale = float(parts[-1].strip("."))
        elif line.startswith("Impact"):
            pass  # Info about impact param
        elif line.startswith("Max"):
            pass  # Info about Max pT scale for MPI
        elif line.startswith("Number of MPI"):
            currentEvent.numMPI = int(parts[4])

    currentEvent.pdf_info = currentPdf
    return currentEvent


def parseStats(block):
    """Parse cross section information, and return object"""
    pass


def parseEventListing(block):
    """Parse full event particle listing, returns list of NodeParticles"""

    # Where particle listing starts and stops
    listingStart = """no        id"""
    listingEnd = """Charge sum"""

    fullEvent = []

    parseLine = False
    for line in block:
        line = line.strip()
        if line.startswith(listingStart):
            parseLine = True
            continue
        elif line.startswith(listingEnd):
            parseLine = False
            continue

        if parseLine:
            print line
            fullEvent.append(parseParticleLine(line))

    return fullEvent


def parseParticleLine(line):
    """Parse line with particle info, and return NodeParticle object"""

    if config.VERBOSE: print line,

    parts = line.split()
    # name = parts[2]
    # d1       = int(parts[6])
    # d2       = int(parts[7])
    flowDict = {}
    if int(parts[8]) or int(parts[9]):
        flowDict[1] = int(parts[8])
        flowDict[2] = int(parts[9])
    particle = NodeParticle(barcode=int(parts[0]),
                            pdgid=int(parts[1]),
                            status=int(parts[3]),
                            mother1=int(parts[4]),
                            mother2=int(parts[5]),
                            px=parts[10],
                            py=parts[11],
                            pz=parts[12],
                            energy=parts[13],
                            mass=parts[14],
                            flowDict=flowDict)

    return particle


def markInteresting(fullEvent, interestingList):
    """Check if particle is in user's interesting list, and if so set colour to
    whatever the ever wanted"""

    for p in fullEvent:
        # Remove any () and test if name in user's interesting list
        for i in interesting:
            if p.getRawName() in i[1]:
                p.isInteresting = True
                p.displayAttributes.colour = i[0]


def addMothers(fullEvent):
    """Add references to mothers based on mother1/2 indicies"""

    for p in fullEvent:
        for m in range(p.m1, p.m2+1):
            p.mothers.append(fullEvent[m])


def addDaughters(fullEvent):
    """Add references to daughters based on mother relationships"""
    # Don't use the daughters in the pythia output, they aren't complete
    # Instead use the mother relationships
    for p in fullEvent:
        for pp in fullEvent:
            if p in pp.mothers and p != pp:
                p.daughters.append(pp)


def removeRedundants(fullEvent):
    """Get rid of redundant particles and rewrite relationships"""

    for p in fullEvent:

        if not p.skip and not p.isInitialState and len(p.mothers) == 1:
            current = p
            mum = p.mothers[0]
            foundSuitableMother = False
            while not foundSuitableMother:
                # Check if mother of current has 1 parent and 1 child,
                # both with same PID. If it does, then it's redundant
                # and we can skip it in future. If not, it's a suitable mother
                # for Particle p
                if (
                    len(mum.mothers) == 1
                    and len(mum.daughters) == 1
                    and mum.PID == mum.mothers[0].PID
                    and mum.PID == current.PID
                ):

                    mum.skip = True
                    current = mum
                    mum = current.mothers[0]
                else:
                    foundSuitableMother = True

            # whatever is stored in mum is the suitable mother for p
            p.mothers[0] = mum
