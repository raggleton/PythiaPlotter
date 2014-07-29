"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

from itertools import izip
from pprint import pprint
import operator

import config  as C # Global definitions
from convertParticleName import convertPIDToTexName, convertPIDToRawName


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


class GenEvent:
    """Class to hold complete event info, e.g. evt number, scales, beam IDs
    as well as list of all particles and vertices"""

    def __init__(self, eventNum=0, numMPI=0, scale=-1.0, alphaQCD=-1.0,
                 alphaQED=-1.0, signalProcessID=0, signalProcessBarcode=0,
                 numVertices=0, beam1Barcode=0, beam2Barcode=0,
                 randomInts=None, weightValues=None):
        self.eventNum = int(eventNum)  # event number
        self.numMPI = int(numMPI)  # number of multi paricle interactions
        self.scale = float(scale)  # event scale
        self.alphaQCD = float(alphaQCD)  # alpha QCD
        self.alphaQED = float(alphaQED)  # alpha QED
        self.signalProcessID = int(signalProcessID)  # signal process id
        self.signalProcessBarcode = int(signalProcessBarcode)  # signal process vertex barcode
        self.numVertices = int(numVertices)  # number of vertices in this event
        self.beam1Barcode = int(beam1Barcode)  # barcode for beam particle 1
        self.beam2Barcode = int(beam2Barcode)  # barcode for beam particle 2
        if not randomInts:
            randomInts = []
        self.randomInts = randomInts  # optional list of random state integers

        # Bit complicated - need to coordinate with Weights class as the
        # weights list in constructor here is actual weight values,
        # but Weight class stores weight names & values as dictionary.
        # Hangover from HepMC
        if not weightValues:
            weightValues = []
        weightValues = [float(w) for w in weightValues]
        self.weightValues = weightValues

        # To hold future objects that conatin info about event e.g. PdfInfo
        self.pdf_info = None
        self.cross_section = None
        self.units = None
        self.weights = None

        # To hold list of vertices and particles
        self.vertices = []
        self.particles = []

    def setWeightNames(self, weightNames=None):
        """Create Weights object atttribute for GenEvent object using the
        weightNames pased in, and weightValues already stored. Stores
        resultant Weights object as GenEvent.weights"""

        if not weightNames:
            weightNames = []
        if len(weightNames) != len(self.weightValues):
            print "ERROR mismatch in number of weight names/values"
        else:
            # strip off annoying leading and trailing " "
            # lovely list comprhension!
            weightNames = [w.strip('"') for w in weightNames]
            # construct a dictionary from weightNames and self.weightValues
            # easy with izip!
            self.weights = Weights(dict(izip(weightNames, self.weightValues)))

    def connectParticlesVertices(self):
        """After getting all GenVertices and Particles from file,
        loop over and sort out Particle/Vertex relationships,
        so that each has lists with references to
        connected Vertices/Particles, respectively.
        Then sort particle list by ascending barcode"""
        # Add vertex reference to particles using stored barcode
        for p in self.particles:
            if p.inVertexBarcode != 0:
                p.inVertex = self.vertices[abs(p.inVertexBarcode)-1]

        self.particles.sort(key=operator.attrgetter('barcode'))

        # Add particle reference to vertices using stored barcodes
        for v in self.vertices:
            for p in self.particles:
                if p.inVertexBarcode == v.barcode:
                    v.inParticles.append(p)
                if p.outVertexBarcode == v.barcode:
                    v.outParticles.append(p)


class Weights:
    """Class to store event weight names and values as dictionary"""

    def __init__(self, weightDict=None):
        if not weightDict:
            weightDict = {}
        self.weightDict = weightDict  # Dictionary of weight names and values


class Units:
    """Class to store momentum and position units"""

    def __init__(self, momentumUnit="GEV", positionUnit="MM"):
        # Check if momentum in MEV or GEV, default to GEV if neither.
        if momentumUnit:
            momentumUnit = momentumUnit.upper()
        if (momentumUnit in ("MEV", "GEV")):
            self.momentumUnit = momentumUnit
        else:
            self.momentumUnit = "GEV"
            print "Momentum must be either MEV or GEV. Defaulting to GEV."

        # Check if momentum in MM or CM, default to MM if neither.
        if positionUnit:
            positionUnit = positionUnit.upper()
        if (positionUnit in ("MM", "CM")):
            self.positionUnit = positionUnit
        else:
            self.positionUnit = "MM"
            print "Position must be either MM or CM. Defaulting to MM."


class GenCrossSection:
    """Class to store cross section + error for event. Units: pb."""

    def __init__(self, crossSection=0.0, crossSectionErr=0.0):
        self.crossSection = float(crossSection)  # cross section in pb
        self.crossSectionErr = float(crossSectionErr)  # error on xsec in pb


class PdfInfo:
    """Class to store parton info (Q scale, momenta, LHAPDF set"""

    def __init__(self, id1=0, id2=0, x1=0, x2=0, scalePDF=0,
                 pdf1=0, pdf2=0, pdf_id1=0, pdf_id2=0):
        self.id1 = int(id1)  # flavour code of first parton
        self.id2 = int(id2)  # flavour code of second parton
        # fraction of beam momentum carried by 1st parton ("beam side")
        self.x1 = float(x1)
        # fraction of beam momentum carried by 2nd parton ("target side")
        self.x2 = float(x2)
        self.scalePDF = float(scalePDF)  # Q-scale used in PDFs (in GeV)
        self.pdf1 = float(pdf1)  # PDF (id1, x1, Q) of the form x*f(x)
        self.pdf2 = float(pdf2)  # PDF (id2, x2, Q) of the form x*f(x)
        self.pdf_id1 = int(pdf_id1)  # LHAPDF set id of first parton
        self.pdf_id2 = int(pdf_id2)  # LHAPDF set id of second parton


class GenVertex:
    """Class to store info about vertex"""

    def __init__(self, barcode=0, id=0, x=0.0, y=0.0, z=0.0, ctau=0.0,
                 numOrphans=0, numOutgoing=0, numWeights=0, weights=None):
        self.barcode = int(barcode)  # barcode
        self.id = int(id)  # id
        self.x = float(x)  # x
        self.y = float(y)  # y
        self.z = float(z)  # z
        self.ctau = float(ctau)  # ctau
        self.numOrphans = int(numOrphans)  # no. of "orphan" incoming particles
        self.numOutgoing = int(numOutgoing)  # no. of outgoing particles
        self.numWeights = len(numWeights)  # no. of entries in weight list
        if not weights:
            weights = []
        weights = [float(w) for w in weights]  # floats not strings!
        self.weights = weights  # optional list of weights

        self.inParticles = []  # Incoming GenParticles
        self.outParticles = []  # Outgoing GenParticles

    def __str__(self):
        pprint(vars(self))
        print "inParticles barcodes:"
        for pi in self.inParticles:
            print(pi.barcode)
        print "outParticles barcodes:"
        for po in self.outParticles:
            print(po.barcode)


class GenParticle:
    """Class to store info about GenParticle in event"""

    def __init__(self, barcode=0, pdgid=0, px=0.0, py=0.0, pz=0.0, energy=0.0,
                 mass=0.0, status=0, polTheta=0.0, polPhi=0.0, flowDict=None):
        self.barcode = int(barcode)  # particle barcode - unique
        self.pdgid = int(pdgid)  # PDGID - see section 43 (?) in PDGID
        self.px = float(px)
        self.py = float(py)
        self.pz = float(pz)
        self.energy = float(energy)  # Units specified in Units.momentumUnit
        self.mass = float(mass)
        self.status = int(status)  # status code
        self.polTheta = float(polTheta)  # polarization theta
        self.polPhi = float(polPhi)  # polarization phi
        self.name = convertPIDToRawName(self.pdgid)  # name in raw form e.g pi0
        self.texname = convertPIDToTexName(self.pdgid)  # name in tex e.g pi^0
        if not flowDict:
            flowDict = {}
        self.flowDict = flowDict  # colour flow
        self.skip = False  # Whether to skip when writing nodes to file
        self.isFinalState = False
        self.isInitialState = False
        self.displayAttributes = DisplayAttributes()

        # Note that other attributes (like in/out vertices,
        # or mother/daughters), are stored in sub-classes Node/EdgeParticle.
        # This is a base class for common attributes.

    def __eq__(self, other):
        return self.barcode == other.barcode

    def __str__(self):
        pprint(vars(self))

    def getRawName(self):
        """Get name without any ( or )"""
        return self.name.translate(None, '()')

class NodeParticle(GenParticle):
    """Subclass to store attributes specially for when particle is represented
    by node, e.g. from Pythia screen output"""

    def __init__(self, barcode=0, pdgid=0, px=0.0, py=0.0, pz=0.0, energy=0.0,
                 mass=0.0, status=0, polTheta=0.0, polPhi=0.0, flowDict=None,
                 mother1=0, mother2=0):

        GenParticle.__init__(barcode=barcode, pdgid=pdgid, px=px, py=py,
                             pz=pz, energy=energy, mass=mass, status=status,
                             polTheta=polTheta, polPhi=polPhi,
                             flowDict=flowDict)

        # For reading in from Pythia screen output, need to read in mother(s)
        # of particle. Can then infer daughters once gathered all particles
        self.m1 = int(mother1)  # barcode of mother 1
        self.m2 = int(mother2)  # barcode of mother 2 (mothers = m1 -> m2?)
        self.mothers = []  # list of NodeParticle objects that are its mother
        self.daughters = []  # list of NodeParticle objects that are its daughters

        # Following only true if reading from Pythia screen output.
        if (self.status > 0):
            self.isFinalState = True

        if ((self.mother1 == 0) and (self.mother2 == 0)):
            self.isInitialState = True

        # Sometimes Pythia sets m2 == 0 if only 1 mother & particle from shower
        # This causes looping issues, so set m2 = m1 if that's the case
        if ((self.mother1 != 0) and (self.mother2 == 0)):
            self.mother2 = self.mother1


class EdgeParticle(GenParticle):
    """Subclass to store attributes specially for when particle is represented
    by edge, e.g. from HepMC"""

    def __init__(self, barcode=0, pdgid=0, px=0.0, py=0.0, pz=0.0, energy=0.0,
                 mass=0.0, status=0, polTheta=0.0, polPhi=0.0, flowDict=None,
                 inVertexBarcode=0, outVertexBarcode=0):

        GenParticle.__init__(barcode=barcode, pdgid=pdgid, px=px, py=py,
                             pz=pz, energy=energy, mass=mass, status=status,
                             polTheta=polTheta, polPhi=polPhi,
                             flowDict=flowDict)

        # Barcode of vertex that has this particle as an incoming particle
        self.inVertexBarcode = int(inVertexBarcode)
        # Reference to GenVertex where this particle is incoming
        self.inVertex = None
        # Barcode of vertex that has this particle as an outgoing particle
        self.outVertexBarcode = int(outVertexBarcode)
        # Reference to GenVertex where this particle is outgoing
        self.outVertex = None


class DisplayAttributes:
    """Class to store attributes about node/edge representation
    of a particle, e.g. node shape, colour"""

    def __init__(self):
        self.isInteresting = False  # Whether the user wants this highlighted
        self.colour = ""  # What colour to highlight the node/edge
        self.shape = "Circle"

