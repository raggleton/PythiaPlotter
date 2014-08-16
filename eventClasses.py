"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

from itertools import izip
from pprint import pprint
import operator

import config as CONFIG  # Global definitions
from convertParticleName import convertPIDToTexName, convertPIDToRawName
import weakref


class GenEvent(object):
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
        self.signalProcessID = int(signalProcessID)  # hard process id
        self.signalProcessBarcode = int(signalProcessBarcode)  # & vtx barcode
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
        # TODO: raise exception if no match? or bad barcode?
        return next((x for x in self.particles if x.barcode == barcode), None)

    def getVertex(self, barcode):
        """Get vertex by its barcode, safer than vertices[i].
        Returns None if no match."""
        return next((x for x in self.vertices if x.barcode == barcode), None)

    def nextVertexBarcode(self):
        """Auto generate next vertex barcode"""
        return "V"+str(len(self.vertices)+1)

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
            # lovely list comprehension!
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
            if p.edge_attr.inVertexBarcode != "V0":
                p.edge_attr.inVertex = \
                    self.getVertex(p.edge_attr.inVertexBarcode)

        self.particles.sort(key=operator.attrgetter('barcode'))

        # Add particle reference to vertices using stored barcodes
        for v in self.vertices:
            for p in self.particles:
                if p.edge_attr.inVertexBarcode == v.barcode:
                    v.inParticles.append(p)
                if p.edge_attr.outVertexBarcode == v.barcode:
                    v.outParticles.append(p)

    def markInitialHepMC(self):
        """After parsing from hepmc, mark initial state vertices/particles.
        These have status = 4"""
        # I guess we could use beam1/2barcode from GenEvent as well?
        for p in self.particles:
            if p.status == 4:
                p.isInitialState = True
                p.edge_attr.isInitialState = True

    def addVerticesForFinalState(self):
        """Add inVertex for final state particles so they can be drawn later."""
        for p in self.particles:
            # if p.isFinalState:
            if p.edge_attr:
                if not p.edge_attr.inVertex:
                    v = GenVertex(barcode=self.nextVertexBarcode())
                    v.inParticles.append(p)
                    v.isFinalState = True
                    self.vertices.append(v)
                    p.edge_attr.setInVertex(v)
                    p.isFinalState = True
            else:
                raise Exception(
                    "ERROR: you haven't given particle EdgeAttributes obj")
            print p.edge_attr.inVertexBarcode

    def addNodeMothers(self):
        """Add references to mothers based on mother1/2 indicies"""
        for p in self.particles:
            if not p.isInitialState:
                # Do some dodgy int <> string casting as Pythia deals in ints,
                # but we generalise to strings to allow NodeToEdge conversions
                for m in range(int(p.node_attr.mother1),
                               int(p.node_attr.mother2)+1):
                    p.node_attr.mothers.append(self.getParticle(barcode=str(m)))

    def addNodeDaughters(self):
        """Add references to daughters based on mother relationships"""
        # Don't use the daughters in the pythia output, they aren't complete
        # Instead use the mother relationships
        for p in self.particles:
            for pp in self.particles:
                if p in pp.node_attr.mothers and p != pp:
                    p.node_attr.daughters.append(pp)

    def removeRedundantNodes(self):
        """Get rid of redundant particles and rewrite relationships
        for particles as Nodes"""
        pass
        # for p in self.particles:
        #     if (not p.skip and not p.isInitialState
        #         and len(p.node_attr.mothers) == 1
        #         and len(p.node_attr.daughters) == 1):
        #
        #         pass
                # if p.node_attr.mothers[0]
            # if (not p.skip and not p.isInitialState
            #         and len(p.node_attr.mothers) == 1):
            #     current = p
            #     mum = p.node_attr.mothers[0]
            #     foundSuitableMother = False
            #     while not foundSuitableMother:
            #         # Check if mother of current has 1 parent and 1 child,
            #         # both with same PID. If it does, then it's redundant
            #         # and we can skip it in future. If not then suitable mother
            #         # for Particle p
            #         if (len(mum.node_attr.mothers) == 1
            #             and len(mum.node_attr.daughters) == 1
            #             and mum.pdgid == mum.node_attr.mothers[0].pdgid
            #             and mum.pdgid == current.pdgid
            #         ):
            #             mum.skip = True
            #             current = mum
            #             mum = current.node_attr.mothers[0]
            #         else:
            #             foundSuitableMother = True
            #
            #     # whatever is stored in mum is the suitable mother for p
            #     p.node_attr.mothers[0] = mum

    def removeRedundantEdges(self):
        """Get rid of redundant particles and rewrite relationships
        for particles as Edges"""
        # TODO: write this. Could be hard!
        pass


class Weights(object):
    """Class to store event weight names and values as dictionary"""

    def __init__(self, weightDict=None):
        if not weightDict:
            weightDict = {}
        self.weightDict = weightDict  # Dictionary of weight names and values


class Units(object):
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


class GenCrossSection(object):
    """class to store cross section + error for event. Units: pb."""

    def __init__(self, crossSection=0.0, crossSectionErr=0.0):
        self.crossSection = float(crossSection)  # cross section in pb
        self.crossSectionErr = float(crossSectionErr)  # error on xsec in pb


class PdfInfo(object):
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


class GenVertex(object):
    """Class to store info about vertex"""

    def __init__(self, barcode="V0", id=0, x=0.0, y=0.0, z=0.0, ctau=0.0,
                 numOrphans=0, numOutgoing=0, numWeights=0, weights=None):
        self.barcode = barcode  # barcode
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
        self.isInitialState = False
        self.isFinalState = False
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

    def __eq__(self, other):
        return self.barcode == other.barcode


class GenParticle(object):
    """Class to store info about GenParticle in event"""

    def __init__(self, barcode="0", pdgid=0, px=0.0, py=0.0, pz=0.0, energy=0.0,
                 mass=0.0, status=0, polTheta=0.0, polPhi=0.0, flowDict=None):
        self.barcode = barcode  # particle barcode - unique
        self.pdgid = int(pdgid)  # PDGID - see section 43 (?) in PDGID
        self.px = float(px)
        self.py = float(py)
        self.pz = float(pz)
        self.energy = float(energy)  # Units specified in Units.momentumUnit
        self.mass = float(mass)
        self.status = int(status)  # status code, diff for Pythia output & hepmc
        self.polTheta = float(polTheta)  # polarization theta
        self.polPhi = float(polPhi)  # polarization phi
        self.name = convertPIDToRawName(self.pdgid)  # name in raw form e.g pi0
        self.texname = convertPIDToTexName(self.pdgid)  # name in tex e.g pi^0
        if not flowDict:
            flowDict = {}
        self.flowDict = flowDict  # color flow
        self.skip = False  # Whether to skip when writing nodes to file
        self.isFinalState = False
        self.isInitialState = False
        self.event = None  # parent event

        # Store color, shape, label, etc
        self.display_attr = DisplayAttributes(self)
        # Store in/out vertices
        self.edge_attr = EdgeAttributes(self)
        # Store mother/daughters
        self.node_attr = NodeAttributes(self)

    def __eq__(self, other):
        return self.barcode == other.barcode

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return '%s' % pprint(vars(self))

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
        v = None  # hold vertex where this particle is outgoing from
        print "Doing particle barcode:", self.barcode
        if self.node_attr.mothers:
            mumVtx = []
            print "Going through mothers"
            for m in self.node_attr.mothers:
                print "mother barcode:", m.barcode
                if m.edge_attr.inVertex:
                    print "inVertex barcode:", m.edge_attr.inVertex.barcode
                    if not m.edge_attr.inVertex in mumVtx:
                        mumVtx.append(m.edge_attr.inVertex)
            # need the if statement as default is None which is an object!
            # find unique ones - could get repetitions
            if len(mumVtx) > 1:
                for mv in mumVtx:
                    print mv.barcode

                raise Exception("Particle: %s has Mothers with >1 invertices!"
                                % (self.barcode))
            elif len(mumVtx) == 1:
                v = mumVtx[0]

        if not v:  # none of mothers has inVertex, so set one up
            print "creating inVertex for mothers"
            v = GenVertex(barcode=event.nextVertexBarcode(), numOutgoing=0)
            for m in self.node_attr.mothers:
                if m.edge_attr.inVertex != v or not m.edge_attr.inVertex:
                    print m.barcode
                    m.edge_attr.setInVertex(v)
                    v.inParticles.append(m)
            event.vertices.append(v)

        # make sure all mothers wired up to vertex
        v.numOutgoing += 1
        v.outParticles.append(self)
        self.edge_attr.outVertex = v
        self.edge_attr.outVertexBarcode = v.barcode

    def convertEdgeToNodeAttributes(self):
        """Convert EdgeAttributes obj to NodeAttributes object"""
        # Add mother barcodes and references first
        mothers = []
        if self.edge_attr.outVertex:  # Get vertex where this is outgoing
            for i in self.edge_attr.outVertex.inParticles:  # Get incoming
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
                self.node_attr.mother1 = mother1
                self.node_attr.mother2 = mother2
                self.node_attr.mothers = mothers

        # Now add daughter references. Don't do barcodes,
        # they aren't guaranteed to be sequential
        if self.edge_attr.inVertex:
            for i in self.edge_attr.inVertex.outParticles:
                if not self.node_attr:
                    self.node_attr = NodeAttributes()
                self.node_attr.daughters.append(i)


class NodeAttributes(object):
    """Class to store attributes specially for when particle is represented
    by node, e.g. from Pythia screen output"""

    def __init__(self, parent, mother1=0, mother2=0):
        self.particle = parent  # ref to parent particle
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


class EdgeAttributes(object):
    """To store attributes specially for when particle is represented
    by edge, e.g. from HepMC"""

    def __init__(self, parent, inVertexBarcode=0, outVertexBarcode=0):
        self.particle = parent  # ref to parent particle
        # Barcode of vertex that has this particle as an incoming particle
        self.inVertexBarcode = inVertexBarcode
        # Reference to GenVertex where this particle is incoming
        self.inVertex = None
        # Barcode of vertex that has this particle as an outgoing particle
        self.outVertexBarcode = outVertexBarcode
        # Reference to GenVertex where this particle is outgoing
        self.outVertex = None

    def __str__(self):
        pprint(vars(self))

    def setInVertex(self, v):
        self.inVertex = v
        self.inVertexBarcode = v.barcode

    def setOutVertex(self, v):
        self.outVertex = v
        self.outVertexBarcode = v.barcode


class DisplayAttributes(object):
    """Class to store attributes about visual node/edge representation
    of a particle, e.g. node shape, color"""

    # TODO: use .format instead of simple string sub
    def __init__(self, parent, rawNames=False):
        self.particle = parent  # ref to parent particle
        # dict to hold attributes & name, so generate_string/getNode|EdgeString
        # are super easy
        self.attr = {}
        self.isInteresting = False  # Whether the user wants this highlighted
        self.rawNames = rawNames  # bool for raw or tex particle names

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return '%s' % pprint(vars(self))

    def setCommonAttributes(self, interestingList=None):
        """Set common display attributes for Nodes & Edges"""
        # Initial/final state common options
        self.attr["color"] = ""
        self.attr["style"] = ""

        if self.particle.isInitialState:
            self.attr["color"] = CONFIG.initial_color
            # self.shape = "circle"
        elif self.particle.isFinalState:
            self.attr["color"] = CONFIG.final_color

        # Set interesting or not
        if interestingList:
            for i in interestingList:
                if self.particle.name in i[1]:
                    self.isInteresting = True
                    self.attr["color"] = i[0]

        # Set label
        if self.rawNames:
            self.attr["label"] = "%s: %s" % (self.particle.barcode,
                                             self.particle.name)
        else:
            self.attr["label"] = self.particle.texname
            self.attr["texlbl"] = "$%s$" % self.particle.texname

    def setAttributesForNode(self, interestingList=None):
        """Set options specifically for NODE plotting mode"""
        # Do node-specific defaults
        self.setCommonAttributes(interestingList)
        self.attr["shape"] = ""
        self.attr["fillcolor"] = self.attr["color"]

        # Set color and shape for initial/final states, or interesting ones
        if self.particle.isInitialState:
            self.attr["style"] = "filled"
            self.attr["shape"] = "circle"
        elif self.particle.isFinalState:
            self.attr["style"] = "filled"
            self.attr["shape"] = "box"
        if self.isInteresting:
            self.attr["style"] = "filled"

    def setAttributesForEdge(self, interestingList=None):
        """Set options specifically for EDGE plotting mode"""
        # Do edge-specific defaults
        self.setCommonAttributes(interestingList)
        self.attr["arrowsize"] = 0.8
        self.attr["fontcolor"] = "black"
        self.attr["penwidth"] = 2  # TODO: currently ignored by dot2tex
        # TikZ options
        if not self.rawNames:
            self.attr["label"] = " "  # space is VITAL!
            if self.particle.pdgid == 22:  # wiggly lines for photons
                self.attr["style"] = "snake=snake"
        if self.isInteresting:
            self.attr["fontcolor"] = self.attr["color"]

    def generate_string(self, attributes):
        """Function to generate string with all necessary attributes.
        attributes is a list of options the user wants to include."""
        attr_string = ""
        for a in attributes:
            if a in self.attr.keys():
                attr_string += a+"=\""+str(self.attr[a])+"\""
                if a != attributes[-1]:
                    attr_string += ", "
            else:
                print "Attribute %s not in the DisplayAttributes object" % a
                continue
        return "["+attr_string+"]"

    def getNodeString(self):
        """Returns string that can be used in GraphViz to describe the node"""
        return self.generate_string(["label", "shape", "style", "fillcolor"])

    def getEdgeString(self):
        """Returns string that can be used in GraphViz to describe the edge"""
        if self.rawNames:
            return self.generate_string(["label",
                                         "color",
                                         "fontcolor",
                                         "arrowsize",
                                         "penwidth"])
        else:
            return self.generate_string(["label",
                                         "texlbl",
                                         "color",
                                         "fontcolor",
                                         "arrowsize",
                                         "style",
                                         "penwidth"])