"""
    Set of method(s) to interpret hepmc file.

    See hepmcformat.txt for reminder, or section 6 of hepMC2 user manual
"""

from eventClasses import *
import config  # Global definitions


def parse(fileName="testSS_HLT.hepmc"):
    """Parse HepMCfile and return collection of events"""

    print "Parsing events from", fileName

    with open(fileName, 'r') as file:

        eventList = []  # To hold all events
        currentEvent = None  # to hold the current GenEvent, to add particles, etc

        for line in file:
            if config.VERBOSE: print line,

            # Get HepMC version
            if line.startswith("HepMC::Version"):
                version = line.split()[1]
                print "Using HepMC version", version

            # Get start of event block
            elif line.startswith("HepMC::IO_GenEvent-START_EVENT_LISTING"):
                print "Start parsing event listing"
            
            # Get end of event block
            elif line.startswith("HepMC::IO_GenEvent-END_EVENT_LISTING"):
                print "End parsing event listing"

            # general GenEvent information            
            elif line.startswith("E"):
                print "Adding GenEvent info"
                currentEvent = parseGenEventLine(line)
                # Done with the old event, add it to the list, start a new one
                if not currentEvent:
                    eventList.append(currentEvent)

            # named weights
            # elif line.startswith("N"):
                # make GenEvent deal with this?
                # weights = parseWeightsLine(line)

            # momentum and position units
            elif line.startswith("U"):
                print "Adding units info"
                currentEvent.units = parseUnitsLine(line)

            # GenCrossSection information: 
            # This line will appear ONLY if GenCrossSection is defined.
            elif line.startswith("C"):
                print "Adding cross-section info"
                currentEvent.cross_section = parseCrossSectionLine(line)

            # HeavyIon information: 
            # This line will contain zeros if there is no associated 
            # HeavyIon object. 
            # We don't use this so ignore (for now). Or throw exception?
            elif line.startswith("H"):
                print "We don't deal with this"

            # PdfInfo information: 
            # This line will contain 0s if there is no associated PdfInfo obj
            elif line.startswith("F"):
                print "Adding pdf info"
                currentEvent.pdf_info = parsePdfInfoLine(line)

            # Need to deal with repetitive vertex and particle                



def parseGenEventLine(line):
    # TODO
    """Parse line from HepMC file containting GenEvent info
    e.g. E 0 -1 3.4651814800093540e+01 1.6059648651865022e-01 7.7326991537120665e-03 123 0 707 1 2 0 1 1.0000000000000000e+00 """
    parts = line.split()

    # parts[11] tells us number of random ints that follow
    # parts[12] to parts[11+numRandom] are the random ints
    # parts[12+numRandom] tells us the number of weights that follow
    # parts[13+numrandom] to the end are the weights
    numRandoms = int(parts[11])
    genE = GenEvent(eventNum=parts[1], numMPI=parts[2], scale=parts[3], 
                    alphaQCD=parts[4], alphaQED=parts[5], 
                    signalProcessID=parts[6], signalProcessBarcode=parts[7], 
                    numVertices=parts[8], beam1Barcode=parts[9], 
                    beam2Barcode=parts[10], randomInts=parts[12:11+numRandoms], 
                    weights=parts[13+numRandoms:])
    return genE

def parseWeightsLine(line):
    # TODO - not vital
    """Parse line from HepMC file containting Weights info
    e.g. N 1 "0" """
    parts = line.split()
    w = Weights()
    return w


def parseUnitsLine(line):
    """Parse line from HepMC file containting Units info
    e.g. U MEV MM """
    parts = line.split()
    u = Units(momentum=parts[1], position=parts[2])
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
    v = GenVertex(barcode=parts[1], id=parts[2],
                  x=parts[3], y=parts[4], z=parts[5], ctau=parts[6],
                  numOrphans=parts[7], numOutgoing=parts[8],
                  numWeights=parts[9], weights=parts[10:])

    return v


def parseGenParticleLine(line):
    """Parse line from HepMC file containing GenParticle info
    e.g. P 4 21 0 0 -2.9355943031880248e+05 2.9355943031880248e+05 0 21 0 0 -3 2 1 102 2 103 """
    parts = line.split()
    
    # TODO: implement optional code index and code for each entry in the flow list
    if parts[13]:
        pass
    # flowDict = {}

    p = GenParticle(barcode=parts[1], pdgid=parts[2],
                    px=parts[3], py=parts[4], pz=parts[5], energy=parts[6],
                    mass=parts[7], status=parts[8], polTheta=parts[9],
                    polPhi=parts[10], vertexBarcode=parts[11])
    return p
