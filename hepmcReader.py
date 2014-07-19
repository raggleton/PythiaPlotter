"""
    Set of method(s) to interpret hepmc file.
    
    See hepmcformat.txt for reminder, or section 6 of hepMC2 user manual
"""

# from eventClasses import Particle

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

            # Get end of event block
            if line.startswith("HepMC::IO_GenEvent-END_EVENT_LISTING"):
                print "End parsing event listing"