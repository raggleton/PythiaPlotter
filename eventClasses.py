"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

from itertools import izip
from pprint import pprint
import operator

import config as C  # Global definitions
from convertParticleName import convertPIDToTexName, convertPIDToRawName

# TODO: Depreciate me
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

        # To hold future objects that contain info about event e.g. PdfInfo
        self.pdf_info = None
        self.cross_section = None
        self.units = None
        self.weights = None

        # To hold list of vertices and particles for easy
        # Or iterate over dictionary?
        self.vertices = []
        self.particles = []

        # To hold dictionary of particles & vertices by barcode
        # key = barcode, value = ref to object
        # self.pDict = {}
        # self.vDict = {}

    # TODO: decorator? See raymond talk
    def getParticle(self, barcode):
        """Get particle by its barcode, safer than particles[i].
        Returns None if no match."""
        return next((x for x in self.particles if x.barcode == barcode), None)

    def getVertex(self, barcode):
        """Get vertex by its barcode, safer than vertices[i].
        Returns None if no match."""
        return next((x for x in self.vertices if x.barcode == barcode), None)

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
            if p.edgeAttributes.inVertexBarcode != 0:
                p.edgeAttributes.inVertex = self.vertices[abs(p.edgeAttributes.inVertexBarcode)-1]

        self.particles.sort(key=operator.attrgetter('barcode'))

        # Add particle reference to vertices using stored barcodes
        for v in self.vertices:
            for p in self.particles:
                if p.edgeAttributes.inVertexBarcode == v.barcode:
                    v.inParticles.append(p)
                if p.edgeAttributes.outVertexBarcode == v.barcode:
                    v.outParticles.append(p)

    def addNodeMothers(self):
        """Add references to mothers based on mother1/2 indicies"""
        for p in self.particles:
            if not p.isInitialState:
                for m in range(p.nodeAttributes.mother1, p.nodeAttributes.mother2+1):
                    p.nodeAttributes.mothers.append(self.particles[m])

    def addNodeDaughters(self):
        """Add references to daughters based on mother relationships"""
        # Don't use the daughters in the pythia output, they aren't complete
        # Instead use the mother relationships
        for p in self.particles:
            for pp in self.particles:
                if p in pp.nodeAttributes.mothers and p != pp:
                    p.nodeAttributes.daughters.append(pp)

    def markInteresting(self, interestingList):
        """Check if particle is in user's interesting list, and if so set colour
        to whatever the ever wanted"""
        for p in self.particles:
            p.markInteresting(interestingList)

    def removeRedundantNodes(self):
        """Get rid of redundant particles and rewrite relationships
        for particles as Nodes"""

        for p in self.particles:

            if (not p.skip and not p.isInitialState
                    and len(p.nodeAttributes.mothers) == 1):
                current = p
                mum = p.nodeAttributes.mothers[0]
                foundSuitableMother = False
                while not foundSuitableMother:
                    # Check if mother of current has 1 parent and 1 child,
                    # both with same PID. If it does, then it's redundant
                    # and we can skip it in future. If not, then suitable mother
                    # for Particle p
                    if (len(mum.nodeAttributes.mothers) == 1
                        and len(mum.daughters) == 1
                        and mum.PID == mum.nodeAttributes.mothers[0].PID
                        and mum.PID == current.PID
                    ):

                        mum.skip = True
                        current = mum
                        mum = current.nodeAttributes.mothers[0]
                    else:
                        foundSuitableMother = True

                # whatever is stored in mum is the suitable mother for p
                p.nodeAttributes.mothers[0] = mum

    def removeRedundantEdges(self):
        """Get rid of redundant particles and rewrite relationships
        for particles as Edges"""
        # TODO: write this. Could be hard!
        pass

    def getInitialParticles(self):
        """Return list of particles that are initial state"""
        initials = []
        for p in self.particles:
            if p.isInitialState and p.pdgid != 90:
                initials.append(p)
        return initials


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
            try:
                momentumUnit = momentumUnit.upper()
            except AttributeError:
                print "ERROR: momentumUnit arg needs to be a string!"
        if (momentumUnit in ("MEV", "GEV")):
            self.momentumUnit = momentumUnit
        else:
            self.momentumUnit = "GEV"
            print "Momentum must be either MEV or GEV. Defaulting to GEV."

        # Check if momentum in MM or CM, default to MM if neither.
        if positionUnit:
            try:
                positionUnit = positionUnit.upper()
            except AttributeError:
                print "ERROR: positionUnit arg needs to be a string!"
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
        self.numWeights = int(numWeights)  # no. of entries in weight list
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

        self.displayAttributes = DisplayAttributes()  # Store colour, shape, etc
        self.edgeAttributes = None  # Store in/out vertices
        self.nodeAttributes = None  # Store mother/daughters


    def __eq__(self, other):
        return self.barcode == other.barcode

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return '%s' % pprint(vars(self))

    def getRawName(self):
        """Get name without any ( or )"""
        return self.name.translate(None, '()')

    def markInteresting(self, interestingList):
        """Check if particle is in user's interesting list, and if so set
        colour to whatever they wanted"""

        # Remove any () and test if name in user's interesting list
        for i in interestingList:
            if self.getRawName() in i[1]:
                self.displayAttributes.isInteresting = True
                self.displayAttributes.colour = i[0]

    def convertNodeToEdgeAttributes(self, event):
        """Convert NodeAttributes object to EdgeAttributes object"""
        # Is there an existing vertex that our particle is outgoing from?
        # (Look in mothers)
        # If there isn't, then create one.
        # - If the particle has mother(s) then assign that new vertex to
        #   be in inVertex of all those mother(s). And do the wiring (set
        #   vertex inParticles = mothers, mothers.inVertex,
        #   mothers.inVertex.barcode)
        # In either scenario, we have a target vertex, and need to set
        # this particle to be the outgoing Particle from that vertex
        #
        # Set vertex barcode as highest vtx barcode in GenEvent+1
        #
        print "ConvertNodeToEdges for particle barcode", self.barcode
        self.edgeAttributes = EdgeAttributes()
        v = None
        mumInVtx = None
        if self.nodeAttributes.mothers:
            mumInVtx = \
                [m.edgeAttributes.inVertex for m in self.nodeAttributes.mothers if m.edgeAttributes.inVertex]  # need the if statement as default is None which is an object!
            print "Num inVtx in", len(self.nodeAttributes.mothers), "mothers", len(mumInVtx)
            # find unique ones - could get repetitions
            if len(mumInVtx) > 1:
                for m in mumInVtx:
                    print m.barcode
                raise Exception("Mothers have >1 invertices!")
            elif len(mumInVtx) == 1:
                v = mumInVtx[0]
        if not v: # none of mothers has invertex, so set one up
            print "creating vertex"
            v = GenVertex(barcode=-1*len(event.vertices), numOutgoing=0)
            for m in self.nodeAttributes.mothers:
                m.edgeAttributes.inVertex = v
                m.edgeAttributes.inVertexBarcode = v.barcode
                v.inParticles.append(m)
            event.vertices.append(v)

        # make sure all mothers wired up to vertex
        v.numOutgoing += 1
        v.outParticles.append(self)
        self.edgeAttributes.outVertex = v
        self.edgeAttributes.outVertexBarcode = v.barcode



    def convertEdgeToNodeAttributes(self):
        """Convert EdgeAttributes obj to NodeAttributes object"""
        # Add mother barcodes and references first
        mothers = []
        if self.edgeAttributes.outVertex:  # Get vertex where this is outgoing
            for i in self.edgeAttributes.outVertex.inParticles:  # Get incoming
                mothers.append(i)
            if mothers:
                mothers = sorted(mothers, key=lambda particle: particle.barcode)
                mother1 = mothers[0].barcode
                mother2 = mothers[-1].barcode
                # Check that we can safely do mothers = mother1, ..., mother2
                for i in mothers:
                    if i.barcode not in range(mother1, mother2+1):
                        print "ERROR: ", i.barcode
                        raise Exception("barcode not in range mother1->mother2")
                self.nodeAttributes = NodeAttributes(mother1, mother2)
                self.nodeAttributes.mothers = mothers

        # Now add daughter references. Don't do barcodes,
        # they aren't guaranteed to be sequential
        if self.edgeAttributes.inVertex:
            for i in self.edgeAttributes.inVertex.outParticles:
                if not self.nodeAttributes:
                    self.nodeAttributes = NodeAttributes()
                self.nodeAttributes.daughters.append(i)


class NodeAttributes:
    """Class to store attributes specially for when particle is represented
    by node, e.g. from Pythia screen output"""

    def __init__(self, mother1=0, mother2=0):

        # For reading in from Pythia screen output, need to read in mother(s)
        # of particle. Can then infer daughters once gathered all particles
        self.mother1 = int(mother1)  # barcode of mother 1
        self.mother2 = int(mother2)  # barcode of mother 2 (mothers = m1 -> m2?)
        self.mothers = []  # list of NodeParticle objects that are its mother
        self.daughters = []  # list of GenParticles that are its daughters

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return "%s, %s, %s" % (self.mother1,
                               self.mother2,
                               self.mothers[0].barcode)


class EdgeAttributes:
    """To store attributes specially for when particle is represented
    by edge, e.g. from HepMC"""

    def __init__(self, inVertexBarcode=0, outVertexBarcode=0):

        # Barcode of vertex that has this particle as an incoming particle
        self.inVertexBarcode = int(inVertexBarcode)
        # Reference to GenVertex where this particle is incoming
        self.inVertex = None
        # Barcode of vertex that has this particle as an outgoing particle
        self.outVertexBarcode = int(outVertexBarcode)
        # Reference to GenVertex where this particle is outgoing
        self.outVertex = None

    def __str__(self):
        pprint(vars(self))


class DisplayAttributes:
    """Class to store attributes about node/edge representation
    of a particle, e.g. node shape, colour"""

    def __init__(self):
        self.isInteresting = False  # Whether the user wants this highlighted
        self.colour = ""  # What colour to highlight the node/edge
        self.shape = "Circle"

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return '%s' % pprint(vars(self))