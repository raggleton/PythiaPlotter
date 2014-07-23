"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

import config  # Global definitions
from convertParticleName import convertPIDToTexName


class Particle:
    """Class to hold particle info in an event listing"""

    def __init__(self, number, PID, name, status, m1, m2):
        # Class instance variables
        self.number = number  # number in fullEvent listing - unique
        self.PID = int(PID)  # PDGID value
        self.name = name  # particle name e.b nu_mu
        self.texname = convertPIDToTexName(PID)  # name in tex e.g pi^0
        self.status = status  # status of particle. If > 0, final state
        self.m1 = int(m1)  # number of mother 1
        self.m2 = int(m2)  # number of mother 2
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

    pass        # PUT STUFF HERE


class GenEvent:
    """Class to hold complete event info, e.g. evt number, scales, beam IDs
    as well as list of all particles and vertices"""

    def __init__(self, eventNum=0, numMPI=0, scale=-1.0, alphaQCD=-1.0,
                 alphaQED=-1.0, signalProcessID=0, signalProcessBarcode=0, 
                 numVertices=0, beam1Barcode=0, beam2Barcode=0, 
                 randomInts=None, weights=None):
        self.eventNum = int(eventNum)  # event number
        self.numMPI = int(numMPI)  # number of multi paricle interactions
        self.scale = float(scale)  # event scale
        self.alphaQCD = float(alphaQCD)  # alpha QCD
        self.alphaQED = float(alphaQED)  # alpha QED
        self.signalProcessID = int(signalProcessID)  # signal process id
        self.signalProcessBarcode = int(signalProcessBarcode)  # barcode for signal process vertex
        self.numVertices = int(numVertices)  # number of vertices in this event
        self.beam1Barcode = int(beam1Barcode)  # barcode for beam particle 1
        self.beam2Barcode = int(beam2Barcode)  # barcode for beam particle 2
        if not randomInts:
            randomInts = []
        self.randomInts = randomInts  # optional list of random state integers
        self.numRandomState = len(self.randomInts)  # number of entries in random state list (may be zero)
        # Bit complicated - need to coordinate with Weights class as the 
        # weight slist in constructor here is actual weight values, 
        # but Weight class stores weight names...
        if not weights:
            weights = []
        self.weights = weights  # optional list of weights
        self.numWeights = len(weights)  # number of entries in weight list (may be zero)
        
        # To hold future objects that conatin info about event e.g. PdfInfo
        self.pdf_info = None
        self.cross_section = None
        self.units = None

        # To hold list of vertices and particles
        self.vertices = []
        self.particles = []

    # TODO: add methods for adding particles and vertices?

class Weights:
    """Class to store named event weights"""
    
    pass


class Units:
    """Class to store momentum and position units"""
    
    def __init__(self, momentum=None, position=None):
        # TODO: enums?
        # self.momentumUnit = "GEV"  # Default to GeV
        # self.positionUnit = "MM"  # Default to MM
        
        momentum = momentum.upper()
        # Check if momentum in MEV or GEV
        if (momentum == "MEV" or momentum == "GEV"):
            self.momentumUnit = momentum
        else:
            self.momentumUnit = "GEV"
            print "Momentum must be either MEV or GEV. Defaulting to GEV."
        
        # Check if momentum in MM or CM
        position = position.upper()
        if (position == "MM" or position == "CM"):
            self.positionUnit = position
        else:
            self.positionUnit = "MM"  # Default to MM
            print "Position must be either MM or CM. Defaulting to MM."


class GenCrossSection:
    """Class to store cross section + error for event. Units: pb."""
    
    def __init__(self, crossSection=0.0, crossSectionErr=0.0):
        self.crossSection = float(crossSection)  # cross section in pb
        self.crossSectionErr = float(crossSectionErr)  # error associated with this cross section in pb


class PdfInfo:
    """Class to store parton info (Q scale, momenta, LHAPDF set"""
    
    def __init__(self, id1=0, id2=0, x1=0, x2=0, scalePDF=0, 
                 pdf1=0, pdf2=0, pdf_id1=0, pdf_id2=0):
        self.id1 = int(id1)  # flavour code of first parton
        self.id2 = int(id2)  # flavour code of second parton
        self.x1 = float(x1)  # fraction of beam momentum carried by first parton ("beam side")
        self.x2 = float(x2)  # fraction of beam momentum carried by second parton ("target side")
        self.scalePDF = float(scalePDF)  # Q-scale used in evaluation of PDFs (in GeV)
        self.pdf1 = float(pdf1)  # PDF (id1, x1, Q) This should be of the form x*f(x)
        self.pdf2 = float(pdf2)  # PDF (id2, x2, Q) This should be of the form x*f(x)
        self.pdf_id1 = int(pdf_id1)  # LHAPDF set id of first parton
        self.pdf_id2 = int(pdf_id2)  # LHAPDF set id of second parton


class GenVertex:
    """Class to store info about vertex"""
    
    def __init__(self, barcode=0, id=0, x=0.0, y=0.0, z=0.0, ctau=0.0, 
                 numOrphans=0, numOutgoing=0, numWeights=0, weights=None):
        self.barcode = int(barcode) # barcode
        self.id = int(id)  # id
        self.x = float(x)  # x
        self.y = float(y)  # y
        self.z = float(z)  # z
        self.ctau = float(ctau)  # ctau
        self.numOrphans = int(numOrphans)  # number of "orphan" incoming particles
        self.numOutgoing = int(numOutgoing)  # number of outgoing particles
        self.numWeights = len(numWeights)  # number of entries in weight list (may be zero)
        if not weights:
            weights = []
        self.weights = weights  # optional list of weights


class GenParticle:
    """Class to store info about GenParticle in event"""

    # TODO: implement optional code index and code for each entry in the flow list
    def __init__(self, barcode=0, pdgid=0, px=0.0, py=0.0, pz=0.0, 
                 energy=0.0, mass=0.0, status=0, polTheta=0.0, polPhi=0.0, 
                 vertexBarcode=0, numFlowList=0):
        self.barcode = int(barcode)
        self.pdgid = int(pdgid)
        self.px = float(px)
        self.py = float(py)
        self.pz = float(pz)
        self.energy = float(energy)
        self.mass = float(mass)
        self.status = int(status)
        self.polTheta = float(polTheta)  # polarization theta
        self.polPhi = float(polPhi)  # polarization phi
        self.vertexBarcode = int(vertexBarcode)
        # self.numFlowList = int(numFlowList)  # number of entries in flow list

