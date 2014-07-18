"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

from convertParticleName import convertPIDToTexName

class Event:
    """Class to hold all info about an event"""

    def __init__():
        print an

class Particle:
    """Class to hold particle info in an event listing"""

    def __init__(self, number, PID, name, status, m1, m2):
        # Class instance variables
        self.number = number  # number in fullEvent listing - unique
        self.PID = int(PID)  # PDGID value
        self.name = name  # particle name e.b nu_mu
        self.texname = convertPIDToTexName(PID)  # name in tex e.g pi^0
        self.status = status  # status of particle. If > 0, final state
        self.m1 = m1  # number of mother 1
        self.m2 = m2  # number of mother 2
        self.skip = False  # Whether to skip when writing nodes to file
        self.mothers = []  # list of Particle objects that are its mother
        self.daughters = []  # list of Particle objects that are its daughters
        self.isInteresting = False  # Whether the user wants this highlighted
        self.nodeColour = ""  # What colour to highlight the node
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

    def __eq__(self, other):
        return self.number == other.number

    def getRawName(self):
        """Get name without any ( or )"""
        return self.name.translate(None, '()')


class EventHeader:
    """Class to hold event header info (GenEventInfo, Weights...),
     not Vertex or Particle"""

    def __init__():
        # PUT STUFF HERE

class GenEventInfo:
    """Class to hold general event info, e.g. evt number, scales, beam IDs"""

    def __init__():


class Weights:
    """Class to store named event weights"""
    
    def __init__():


class Units:
    """Class to store momentum and position units"""
    
    def __init__(momentum, position):
        # TODO: enums?
        self.momentumUnit = "GEV"  # Default to GeV
        self.positionUnit = "MM"  # Default to MM
        
        # Check if momentum in MEV or GEV
        if (upper(momentum) == "MEV" or upper(momentum) == "GEV"):
            self.momentumUnit = upper(momentum)
        else:
            print "Momentum must be either MEV or GEV. Defaulting to GEV."
        
        # Check if momentum in MM or CM
        if (upper(position) == "MM" or upper(position) == "CM"):
            self.positionUnit = upper(position)
        else:
            print "Position must be either MM or CM. Defaulting to MM."


class GenCrossSection:
    """Class to store cross section + error for event"""
    
    def __init__():


class PdfInfo:
    """Class to store parton info (Q scale, momenta, LHAPDF set"""
    
    def __init__():


class GenVertex:
    """Class to store info about vertex"""
    
    def __init__():