"""
    Set of method(s) to interpret hepmc file.

    See hepmcformat.txt for reminder, or section 6 of hepMC2 user manual
"""

from eventClasses import *

verbose = True


def parse(fileName="testSS_HLT.hepmc"):
    """Parse HepMCfile and return collection of events"""

    print "Parsing events from ", fileName

    with open(fileName, 'r') as file:

        for line in file:
            if verbose: print line,

            # Get HepMC version
            if line.startswith("HepMC::Version"):
                version = line.split()[1]
                print "Using HepMC version", version

            # Get start of event block
            if line.startswith("HepMC::IO_GenEvent-START_EVENT_LISTING"):
                print "Start parsing event listing"

            # general GenEvent information            
            if line.startswith("E"):
                genEvent = parseGenEventLine(line)

            # named weights
            if line.startswith("N"):
                weights = parseWeightsLine(line)

            # momentum and position units
            if line.startswith("U"):
                units = parseUnitsLine(line)

            # GenCrossSection information: 
            # This line will appear ONLY if GenCrossSection is defined.
            if line.startswith("C"):
                genCrossSection = parseCrossSectionLine(line)

            # HeavyIon information: 
            # This line will contain zeros if there is no associated 
            # HeavyIon object. 
            # We don't use this so ignore (for now)
            if line.startswith("H"):
                print "We don't deal with this"
                pass

            # PdfInfo information: 
            # This line will contain 0s if there is no associated PdfInfo obj
            if line.startswith("F"):
                pdfInfo = parsePdfInfoLine(line)

            # Get end of event block
            if line.startswith("HepMC::IO_GenEvent-END_EVENT_LISTING"):
                print "End parsing event listing"


def tidyLineRemoveKey(line, key):
    """Tidy up line from file for searching (extra spaces, etc) and remove
    the Line Key (e.g. P, V) from the start to allow further processing"""

    strippedline = line.strip()


def parseGenEventLine(line):
    """Parse line from HepMC file containting GenEvent info
    e.g. """
    parts = line.split()


def parseWeightsLine(line):
    """Parse line from HepMC file containting Weights info
    e.g."""
    parts = line.split()


def parseUnitsLine(line):
    """Parse line from HepMC file containting Units info
    e.g. U MEV MM"""
    parts = line.split()
    units = Units(parts[1], parts[2])
    return units


def parseCrossSectionLine(line):
    """Parse line from HepMC file containting CrossSection info
    e.g. C 1.5299242538371922e+06 4.4721515953955459e+04"""
    parts = line.split()


def parsePdfInfoLine(line):
    """Parse line from HepMC file containting PdfInfo info
    e.g."""
    parts = line.split()

def parseGenVertexLine(line):
    """Parse line from HepMC file containing GenVertex info
    e.g."""
    pass


def parseGenParticleLine(line):
    """Parse line from HepMC file containing GenParticle info"""
    pass