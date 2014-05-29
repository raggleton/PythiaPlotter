#!/usr/bin/python
#
import sys
from subprocess import call
#
# Script that converts the event listing from Pythia
# into a Graphviz file to be plotted with dot
# e.g.
# python makeGraphFromPythia.py
# dot -Tpdf myExampleEvent.gv -o myExampleEvent.pdf
#
# Note, you can get this script to do both steps for you! (see doDot option)
#
###############################################################################
# Edit the following:
###############################################################################
#
# Filename for input txt file with Pythia listing
# inputFilename = "testLine.txt"
inputFilename = "qcdScatterSmall.txt"
#
# Filename for output graphviz file
gvFilename = "myExampleEvent.gv"
#
# Option to do the dot stage as well
doDot = True
#
# Filename for output PDF
# Note, if you don't define one but doDot == True, it will automatically create
# a filename using gvFilename
pdfFilename = ""
#
# Interesting particles we wish to highlight
# include antiparticles
interesting = ["tau+", "tau-", "mu+", "mu-"]
#
# Option to remove redundant particles from graph.
# Useful for cleaning up the graph, but don't enable if you want to debug the
# event listing or see where recoil/shower gluons are.
removeRedundants = True
#
###############################################################################
# DO NOT EDIT ANYTHING BELOW HERE
###############################################################################


class Particle:
    """Class to hold particle info in an event listing"""

    def __init__(self, number, PID, name, status, m1, m2):
        # Class instance variables
        self.number = number  # number in fullEvent listing - unique
        self.PID = PID  # PDGID value
        self.name = name  # particle name e.b nu_mu
        self.status = status  # status of particle. If > 0, final state
        self.m1 = m1  # number of mother 1
        self.m2 = m2  # number of mother 2
        self.skip = False  # Whether to skip when writing nodes to file
        self.mothers = []  # list of Particle objects that are its mother
        self.daughters = []  # list of Particle objects that are its daughters
        self.isInteresting = False  # Whether the user wants this highlighted
        self.isFinalState = False
        self.isInitialState = False

        if (status > 0):
            self.isFinalState = True

        if ((m1 == 0) and (m2 == 0)):
            self.isInitialState = True

        # Sometimes Pythia sets m2 == 0 if only 1 mother & particle from shower
        # This causes looping issues, so set m2 = m1 if that's the case
        if ((m1 != 0) and (m2 == 0)):
            self.m2 = m1

        if self.name.translate(None, '()') in interesting:
            self.isInteresting = True

    def __eq__(self, other):
        return self.number == other.number

    def getRawName(self):
        """Get name without any ( or )"""
        return self.name.translate(None, '()')

###############################################################################
# MAIN BODY OF CODE HERE
###############################################################################

# List of Particle objects in hard and full events,
# in order of number in event listing.
# So the object at fullEvent[i] has self.number = i
fullEvent = []
hardEvent = []

# To hold all the initial state particles that should be aligned
sameInitialOnes = []

# For debugging - print output to screen as well as file
verbose = False

# Open input file & parse event info
with open(inputFilename, "r") as inputFile:

    print "Reading event listing from %s" % inputFilename

    # For processing the full output from Pythia - need to know where
    # event listing starts and stops
    listingStart = """no        id"""
    listingEnd = """Charge sum"""

    doneHardEvent = False
    doneFullEvent = False
    parseLine = False

    # Read in file to list of Particles
    for line in inputFile:
        # Parse each line, looking for the start or end of event listing
        strippedLine = line.strip()
        if strippedLine.startswith(listingStart):
            parseLine = True
            continue
        elif strippedLine.startswith(listingEnd):
            parseLine = False
            if not doneHardEvent:
                doneHardEvent = True
            elif not doneFullEvent:
                doneFullEvent = True
            continue

        if parseLine:

            if verbose: print line

            values = line.split()
            number = int(values[0])
            PID = int(values[1])
            name = values[2]
            status = int(values[3])
            m1 = int(values[4])
            m2 = int(values[5])
            # d1       = int(values[6])
            # d2       = int(values[7])
            particle = Particle(number, PID, name, status, m1, m2)

            if particle.isInitialState:
                sameInitialOnes.append(particle)

            if not doneHardEvent:
                hardEvent.append(particle)
            elif not doneFullEvent:
                fullEvent.append(particle)

    print "Done reading file"

# Add references to mothers
for p in fullEvent:
    for m in range(p.m1, p.m2+1):
        p.mothers.append(fullEvent[m])

# Add references to daughters
# Don't use the daughters in the pythia output, they aren't complete
# Instead use the mother relationships
for p in fullEvent:
    for pp in fullEvent:
        if p in pp.mothers and p != pp:
            p.daughters.append(pp)

# Get rid of redundant particles
# and rewrite mothers
if removeRedundants:
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

# Write relationships to graphviz file
with open(gvFilename, "w") as gvFile:

    print "Writing graphviz file to %s" % gvFilename

    # Now process all the particles and add appropriate links to graphviz file
    # Start from the end and work backwards to pick up all connections
    # (doesn't work if you start at beginning and follow daughters)
    gvFile.write("digraph g {\n    rankdir = RL;\n")
    for p in reversed(fullEvent):
        # if p.number < 901:
        if p.skip:
            continue

        pNumName = '"%s:%s"' % (p.number, p.name)
        entry = '  %s -> { ' % pNumName

        for m in p.mothers:
            entry += '"%s:%s" ' % (m.number, m.name)

        entry += "} [dir=\"back\"]\n"

        if verbose: print entry
        gvFile.write(entry)

        # Set special features for initial/final state & interesting particles
        # Final state: box, yellow fill
        # Initial state: circle (default), green fill
        # Interesting: red fill (overrides green/yellow fill)
        config = ""
        if p.isInteresting or p.isFinalState or p.isInitialState:
            colour = ""
            shape = "box"
            if p.isInteresting:
                colour = "red"
            else:
                if p.isFinalState:
                    colour = "yellow"
                elif p.isInitialState:
                    colour = "green"
                    shape = "circle"

            config = '  %s [label=%s, shape=%s, style=filled, fillcolor=%s]\n'\
                % (pNumName, pNumName, shape, colour)

        if config:
            gvFile.write(config)
            if verbose: print config

    # Set all initial particles to be level in diagram
    rank = "  {rank=same;"
    for s in sameInitialOnes:
        rank += '"%s:%s" ' % (s.number, s.name)
    gvFile.write(rank+"} // Put initial particles on same level\n")
    gvFile.write("}")

# Run dot to produce the PDF
if pdfFilename == "":
    pdfFilename = gvFilename.replace(".gv", ".pdf")
if doDot:
    print "Producing PDF %s" % pdfFilename
    call(["dot","-Tpdf",gvFilename,"-o", pdfFilename])
