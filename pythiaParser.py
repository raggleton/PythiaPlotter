"""
For parsing the output of PYTHIA8 that it prints to screen.

"""
from pprint import pprint

# PythiaPlotter files
from eventClasses import *
import config  # For my Global definitions


def parse(filename="qcdScatterSmall.txt"):
    """Parse PYTHIA8 screen output and return event full of NodeParticles"""

    currentEvent = GenEvent()

    # List of Particle objects in full event,
    # in order of number in event listing.
    # So the object at fullEvent[i] has self.barcode = i
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

        doneHardEvent = False
        doneFullEvent = False
        parseLine = False

        # To hold list of lines for parsing in separate methods
        addToBlock = False
        block = []

        # Read in file to list of Particles
        for line in inputFile:
            strippedLine = line.strip()

            if addToBlock:
                block.append(line)
            
            # Go through file, looking for matches to triggers
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
                parseEventListing(block, currentEvent)
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
    pass


def parseStats(block):
    """Parse cross section information, and return object"""
    pass

def parseEventListing(block, genEvent):
    """Parse full event particle listing"""
    
    # Where particle listing starts and stops
    listingStart = """no        id"""
    listingEnd = """Charge sum"""

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
            # genEvent.particles.append(parseParticleLine(line))


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
