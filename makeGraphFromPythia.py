#!/usr/bin/python
#
import sys
#
# Script that converts the event listing from Pythia
# into a Graphviz file to be plotted with dot
# e.g.
# python makeGraphFromPythia.py
# dot -Tpdf myEvent2.gv -o myEvent2.pdf

###############################################################################
# Edit the following:
###############################################################################
#
# Filename for input txt file with Pythia listing
inputFilename = "testLine.txt"
#
# Filename for output graphviz file
outputFilename = "myEvent2.gv"
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
        self.number = number  # number in event listing - unique
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

# List of Particle objects in event, in order of number in event listing
# So the object at event[i] has self.number = i
event = []

# To hold all the initial state particles that should be aligned
sameInitialOnes = []

# For debugging - print output to screen as well as file
verbose = False

# Open input/output files
try:    
    inputFile = open(inputFilename, "r")
except IOError:    
    sys.exit("Error opening %s: can\'t find file or read data" % inputFilename)
else:
    print "Reading event listing from %s" % inputFilename

try: 
    outFile = open(outputFilename, "w")
except IOError:
    sys.exit("Error opening %s: can\'t find file or write data" % outputFilename)
else: 
    print "Writing graphviz file to %s" % outputFilename
    

# Read in file to list of Particles
for line in inputFile:
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

    event.append(particle)

# Add references to mothers
for p in event:
    for m in range(p.m1, p.m2+1):
        p.mothers.append(event[m])

# Add references to daughters
# Don't use the daughters in the pythia output, they aren't complete
# Instead use the mother relationships
for p in event:
    for pp in event:
        if p in pp.mothers and p != pp:
            p.daughters.append(pp)

# Get rid of redundant particles
# and rewrite mothers
if removeRedundants:
    for p in event:

        if not p.skip and not p.isInitialState and len(p.mothers) == 1:

            current = p
            mum = p.mothers[0]
            foundSuitableMother = False
            while not foundSuitableMother:

                # Check if mother of current has 1 parent and 1 child,
                # both with same PID. If it does, then it's redundant
                # and we can skip it in future. If not, it's a suitable mother
                # for Particle p
                if (len(mum.mothers) == 1
                    and len(mum.daughters) == 1
                    and mum.PID == mum.mothers[0].PID
                    and mum.PID == current.PID):

                    mum.skip = True
                    current = mum
                    mum = current.mothers[0]
                else:
                    foundSuitableMother = True

            # whatever is stored in mum is the suitable mother for p
            p.mothers[0] = mum

# Now process all the particles and add appropriate links to graphviz file
# Start from the end and work backwards to pick up all connections
# (doesn't work if you start at beginning and follow daughters)
outFile.write("digraph g {\n    rankdir = RL;\n")
for p in reversed(event):
    # if p.number < 901:
    if p.skip:
        continue

    pNumName = '"%s:%s"' % (p.number, p.name)
    entry = '    %s -> { ' % pNumName

    for m in p.mothers:
        entry += '"%s:%s" ' % (m.number, m.name)

    entry += "} [dir=\"back\"]\n"

    if verbose: print entry
    outFile.write(entry)

    # Define special features for initial, final state & interesting particles
    # Final state: box, yellow fill
    # Initial state: circle (default), green fill
    # Interesting: red fill (overrides green/yellow fill)
    config = ""
    if p.isInteresting or p.isFinalState or p.isInitialState:
        colour = ""
        if p.isInteresting:
            colour = "red"
        else:
            if p.isFinalState:
                colour = "yellow"
            elif p.isInitialState:
                colour = "green"

        config = '    %s [label=%s, shape=box, style=filled, fillcolor=%s]\n' \
            % (pNumName, pNumName, colour)

    if config:
        outFile.write(config)
        if verbose: print config

# Set all initial particles to be level in diagram
rank = "    {rank=same;"
for s in sameInitialOnes:
    rank += '"%s:%s" ' % (s.number, s.name)
outFile.write(rank+"} // Put initial particles on same level\n")

outFile.write("}")

# Clean up
inputFile.close()
outFile.close()
