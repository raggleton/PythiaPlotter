"""
    Set of method(s) to interpret hepmc file.

    See hepmcformat.txt for reminder, or section 6 of hepMC2 user manual
"""

from itertools import izip
from pprint import pprint

# PythiaPlotter files
from eventClasses import *
import config as CONFIG

# TODO: delete all the unnecessary if CONFIG.VERBOSE: print vars() lines


def parse(filename="test/testSamples/testSS_HLT.hepmc", eventNumber=0):
    """Parse HepMCfile and return eventNumber GenEvent.
    Note that eventNumber starts at 0, not 1.
    Defaults to first event if eventNumber unspecified."""

    with open(filename, 'r') as file:

        print "Parsing events from", filename

        eventList = []  # To hold all events
        currentEvent = None  # hold current GenEvent, add particles, etc
        currentVertex = None  # hold current vertex, to add ref to particles
        for line in file:
            # if CONFIG.VERBOSE: print line,

            # Get HepMC version
            if line.startswith("HepMC::Version"):
                version = line.split()[1]
                if CONFIG.VERBOSE: print "Using HepMC version", version

            # Get start of event block
            elif line.startswith("HepMC::IO_GenEvent-START_EVENT_LISTING"):
                print "Start parsing event listing"

            # Get end of event block,
            # add vertex references to GenParticles & vice versa,
            # and add the last GenEvent
            elif line.startswith("HepMC::IO_GenEvent-END_EVENT_LISTING"):
                postProcessEvent(currentEvent, eventList)
                if CONFIG.VERBOSE:
                    print "Adding GenEvent to list"
                if CONFIG.VERBOSE:
                    print len(currentEvent.particles), len(currentEvent.vertices)
                print "End parsing event listing"

            # general GenEvent information
            elif line.startswith("E"):
                # Done with the old event, add it to the list, start a new one
                if currentEvent:
                    postProcessEvent(currentEvent, eventList)
                    # if CONFIG.VERBOSE: print vars(currentEvent)
                    if CONFIG.VERBOSE: print "Adding GenEvent to list"
                    if CONFIG.VERBOSE: print len(currentEvent.particles),
                    len(currentEvent.vertices)
                currentEvent = parseGenEventLine(line)
                if CONFIG.VERBOSE: print "*** EVENT: Adding GenEvent info"

            # named weights
            elif line.startswith("N"):
                # line.split()[1] has the number of weights
                # line.split()[2:] has all the weight names
                currentEvent.setWeightNames(line.split()[2:])
                if CONFIG.VERBOSE: print "Adding weights info"
                if CONFIG.VERBOSE: print pprint(vars(currentEvent.weights))

            # momentum and position units
            elif line.startswith("U"):
                currentEvent.units = parseUnitsLine(line)
                if CONFIG.VERBOSE: print "Adding units info"
                if CONFIG.VERBOSE: print pprint(vars(currentEvent.units))

            # GenCrossSection information:
            # This line will appear ONLY if GenCrossSection is defined.
            elif line.startswith("C"):
                currentEvent.cross_section = parseCrossSectionLine(line)
                if CONFIG.VERBOSE: print "Adding cross-section info"
                if CONFIG.VERBOSE: print pprint(vars(currentEvent.cross_section))

            # HeavyIon information:
            # This line will contain zeros if there is no associated
            # HeavyIon object.
            # We don't use this so ignore (for now). Or throw exception?
            elif line.startswith("H"):
                if CONFIG.VERBOSE: print "We don't deal with this"

            # PdfInfo information:
            # This line will contain 0s if there is no associated PdfInfo obj
            elif line.startswith("F"):
                currentEvent.pdf_info = parsePdfInfoLine(line)
                if CONFIG.VERBOSE: print "Adding pdf info"
                if CONFIG.VERBOSE: print pprint(vars(currentEvent.pdf_info))

            # GenVertex information:
            # Need to keep track of last process vertex to add to GenParticle
            elif line.startswith("V"):
                v = parseGenVertexLine(line)
                currentEvent.vertices.append(v)
                currentVertex = v
                if CONFIG.VERBOSE: print "Adding GenVertex info"
                # if CONFIG.VERBOSE: pprint(vars(v))

            # GenParticle information:
            # The GenVertex line before this has this particle as outgoing
            elif line.startswith("P"):
                p = parseGenParticleLine(line)
                # Add outVertices and barcodes
                p.edge_attr.outVertexBarcode = currentVertex.barcode
                p.edge_attr.outVertex = currentVertex
                currentEvent.particles.append(p)
                if CONFIG.VERBOSE: print "Adding GenParticle info"
                # if CONFIG.VERBOSE: pprint(vars(p))

        if CONFIG.VERBOSE: print len(eventList)
        if CONFIG.VERBOSE: pprint(vars(currentEvent))

    return eventList[eventNumber]


def parseGenEventLine(line):
    """Parse line from HepMC file containting GenEvent info
    e.g. E 0 -1 3.4651814800093540e+01 1.6059648651865022e-01 7.7326991537120665e-03 123 0 707 1 2 0 1 1.0000000000000000e+00 """
    parts = line.split()

    # parts[11] tells us number of random ints that follow
    # parts[12] to parts[11+numRandom] are random ints (end value is exclusive)
    # parts[12+numRandom] tells us the number of weights that follow
    # parts[13+numrandom] to the end are the weights
    numRandoms = int(parts[11])
    genE = GenEvent(eventNum=parts[1], numMPI=parts[2], scale=parts[3],
                    alphaQCD=parts[4], alphaQED=parts[5],
                    signalProcessID=parts[6], signalProcessBarcode=parts[7],
                    numVertices=parts[8], beam1Barcode=parts[9],
                    beam2Barcode=parts[10], randomInts=parts[12:12+numRandoms],
                    weightValues=parts[13+numRandoms:])
    return genE


def parseUnitsLine(line):
    """Parse line from HepMC file containting Units info
    e.g. U MEV MM """
    parts = line.split()
    u = Units(momentumUnit=parts[1], positionUnit=parts[2])
    return u


def parseCrossSectionLine(line):
    """Parse line from HepMC file containting CrossSection info
    e.g. C 1.5299242538371922e+06 4.4721515953955459e+04 """
    parts = line.split()
    c = GenCrossSection(crossSection=parts[1], crossSectionErr=parts[2])
    return c


def parsePdfInfoLine(line):
    """Parse line from HepMC file containting PdfInfo info
    e.g. F 21 21 2.9758908919249000e-03 7.3389857579700624e-02 3.4651814800093540e+01 1.7560069564760610e+01 1.3634687138200170e+00 0 0 """
    parts = line.split()
    f = PdfInfo(id1=parts[1], id2=parts[2], x1=parts[3], x2=parts[4],
                scalePDF=parts[5], pdf1=parts[6], pdf2=parts[7],
                pdf_id1=parts[8], pdf_id2=parts[9])
    return f


def parseGenVertexLine(line):
    """Parse line from HepMC file containing GenVertex info
    e.g. V -3 0 0 0 0 0 0 2 0 """
    parts = line.split()
    v = GenVertex(barcode=parts[1].replace("-", "V"), id=parts[2],
                  x=parts[3], y=parts[4], z=parts[5], ctau=parts[6],
                  numOrphans=parts[7], numOutgoing=parts[8],
                  numWeights=parts[9], weights=parts[10:])
    return v


def parseGenParticleLine(line):
    """Parse line from HepMC file containing GenParticle info
    e.g. P 4 21 0 0 -2.9355943031880248e+05 2.9355943031880248e+05 0 21 0 0 -3 2 1 102 2 103 """
    parts = line.split()
    # Handle flow entries at end, e.g. 2 1 102 2 103 from above
    # The first number (parts[12]) is the number of entries in flow list
    # The following numbers (parts[13:]) are pairs of code index and code for
    # each entry in the flow list. We use the "stride" feature of ranges,
    # [start:stop:step], list comprehension to convert to ints,
    # izip to turn into pairs, then cast to dictionary. Sweet!
    flowDict = dict(izip([int(x) for x in parts[13::2]],
                         [int(y) for y in parts[14::2]]))
    p = GenParticle(barcode=parts[1], pdgid=parts[2],
                    px=parts[3], py=parts[4], pz=parts[5], energy=parts[6],
                    mass=parts[7], status=parts[8], polTheta=parts[9],
                    polPhi=parts[10], flowDict=flowDict)
    p.edge_attr.inVertexBarcode = parts[11].replace("-", "V")
    return p


def postProcessEvent(currentEvent, eventList):
    """After getting GenEvent, do common things"""
    currentEvent.connectParticlesVertices()
    # for p in currentEvent.particles:
    #     p.convertEdgeToNodeAttributes()
    # currentEvent.markInitialHepMC()
    eventList.append(currentEvent)