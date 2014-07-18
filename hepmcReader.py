"""
    Set of method(s) to interpret hepmc file.
    
    See hepmcformat.txt for reminder, or section 6 of hepMC2 user manual
"""

from eventClasses import Particle

verbose = True

def parseHepMCFile(fileName):
    """Parse HepMCfile and return collection of events"""
    
    print "Parsing events from ", fileName
    
    with open(fileName, 'r') as file:
        for line in file:
            if verbose: print line