"""
    This stores all the classes used in event handling, e.g. particle class,
    event class. Based on HepMC, so lots of classes should have similar names
"""

from itertools import izip
from pprint import pprint

import config as CONFIG
from convertParticleName import convertPIDToTexName, convertPIDToRawName


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
        return "V" + str(len(self.vertices) + 1)

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

        # self.particles.sort(key=operator.attrgetter('barcode'))
        self.particles.sort(key=lambda a: int(a.barcode))

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
                # Pythia has a self-loop for initial particles, bit annoying
                # create a new vertex for proton to come out of
                if p.edge_attr.inVertex == p.edge_attr.outVertex:
                    p.edge_attr.outVertex.numOutgoing -= 1
                    p.edge_attr.outVertex.outParticles.remove(p)
                    v = GenVertex(barcode=self.nextVertexBarcode(),
                                  numOutgoing=1)
                    v.isInitialState = True
                    v.outParticles = p
                    p.edge_attr.outVertex = v
                    p.edge_attr.outVertexBarcode = v.barcode
                    self.vertices.append(v)

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

    def addNodeMothers(self):
        """Add references to mothers based on mother1/2 indicies"""
        for p in self.particles:
            if not p.isInitialState:
                # Do some dodgy int <> string casting as Pythia deals in ints,
                # but we generalise to strings to allow NodeToEdge conversions
                for m in range(int(p.node_attr.mother1),
                               int(p.node_attr.mother2) + 1):
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
        # Mark particles as redundant if:
        # - only 1 mother, same pdgid
        # - only 1 daughter, same pdgid
        # - not initial or final state
        for p in self.particles:
            if (not p.skip and not p.isInitialState and not p.isFinalState
                and len(p.node_attr.mothers) == 1
                and p.node_attr.mothers[0].pdgid == p.pdgid
                and p.node_attr.daughters[0].pdgid == p.pdgid
                and len(p.node_attr.daughters) == 1):

                p.isRedundant = True
                p.skip = True
                mother = p.node_attr.mothers[0]
                child = p.node_attr.daughters[0]
                # Rewire as if p never existed
                mother.node_attr.daughters.remove(p)
                mother.node_attr.daughters.append(child)
                child.node_attr.mothers.remove(p)
                child.node_attr.mothers.append(mother)

    def removeRedundantEdges(self):
        """Get rid of redundant particles & vertices and rewrite relationships
        for particles as Edges"""
        # Mark particle as redundant if:
        # - its outVertex only has 1 particle out (itself)
        # - its outVertex only has 1 particle in, with same pdgid
        # - isn't initial or final state
        for p in self.particles:
            if (len(p.edge_attr.outVertex.inParticles) == 1
                and p.edge_attr.outVertex.inParticles[0].pdgid == p.pdgid
                and len(p.edge_attr.outVertex.outParticles) == 1
                and not p.isInitialState and not p.isFinalState):

                # Get rid of the particle and its outVertex.
                # Also remove it from its inVertex inParticles list
                # Rewire so any incoming particle now uses p.inVertex
                # as their inVertex, and update that vertex
                p.skip = True
                p.edge_attr.outVertex.skip = True
                incoming = p.edge_attr.outVertex.inParticles[0]
                incoming.edge_attr.setInVertex(p.edge_attr.inVertex)
                p.edge_attr.inVertex.inParticles.remove(p)
                p.edge_attr.outVertex.skip = True

    def convertNodesToEdges(self):
        """Converts from Node representation to Edge representation"""
        pass
        # for p in self.particles:
        # if len(p.node_attr.mothers) <= 1:
        #         # If our particle has 0 or 1 mothers then we can proceed easily.
        #         # Check if the mother has an inVertex, if so use that for p
        #         # If not, create one and assign it to mother and p
        #         v = None
        #         in_p = None
        #         if p.node_attr.mothers:
        #             in_p = p.node_attr.mothers[0]
        #             if p.node_attr.mothers[0].edge_attr.inVertex:
        #                 v = p.node_attr.mothers[0].edge_attr.inVertex
        #
        #         self.create_assign_to_vtx(vertex=v, in_p=in_p, out_p=p)
        #     else:
        #         # If our particle has more than 1 mother, more difficult.
        #         # To tackle this, we look for mothers that have non-common
        #         # daughters (this is hard?)
        #         # Then for each of those, we create duplicate particles
        #         # and necessary vertices (and do the wiring).
        #         # Then we hook up the rest of the mothers.
        #         for m in p.node_attr.mothers:

    def create_assign_to_vtx(self, vertex=None, in_p=None, out_p=None):
        """Simple method to create a new GenVertex if necessary,
        and assign in_p as incoming particle and out_p as outgoing particle,
        doing all the necessary wiring"""
        if not vertex:
            vertex = GenVertex(barcode=self.nextVertexBarcode())
            self.vertices.append(vertex)
        if out_p:
            out_p.edge_attr.outVertex = vertex
            out_p.edge_attr.outVertexBarcode = vertex.barcode
            vertex.numOutgoing += 1
            vertex.outParticles.append(out_p)
        if in_p:
            in_p.edge_attr.inVertex = vertex
            in_p.edge_attr.inVertexBarcode = vertex.barcode
            vertex.inParticles.append(in_p)


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
        self.skip = False  # skip when iterating over list of vertices
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
        self.isRedundant = False
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
        print self.barcode

    def __repr__(self):
        return '%s' % self.barcode

    def convertNodeToEdgeAttributes(self, event):
        """Convert NodeAttributes object to EdgeAttributes object"""
        # Is there an existing vertex that our particle is outgoing from?
        # (Look in mothers)
        # If there isn't, then create one.
        # - If the particle has mother(s) then assign that new vertex to
        # be in inVertex of all those mother(s). And do the wiring (set
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
                mother1 = int(mothers[0].barcode)
                mother2 = int(mothers[-1].barcode)
                # Check that we can safely do mothers = mother1, ..., mother2
                for i in mothers:
                    if i.barcode not in range(mother1, mother2 + 1):
                        print "ERROR: ", i.barcode
                        print mother1, mother2 + 1
                        raise Exception("barcode not in range mother1->mother2")
                self.node_attr.mother1 = str(mother1)
                self.node_attr.mother2 = str(mother2)
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

    def __init__(self, parent, mother1="", mother2=""):
        self.particle = parent  # ref to parent particle
        # For reading in from Pythia screen output, need to read in mother(s)
        # of particle. Can then infer daughters once gathered all particles
        self.mother1 = mother1  # barcode of mother 1
        self.mother2 = mother2  # barcode of mother 2 (mothers = m1 -> m2?)
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

    def __init__(self, parent, inVertexBarcode="", outVertexBarcode=""):
        self.particle = parent  # ref to parent particle
        # Barcode of vertex that has this particle as an incoming particle
        # Only used when doing hepmc parsing, for everything else use
        # self.inVertex.barcode as conssitent
        self.inVertexBarcode = inVertexBarcode
        # Reference to GenVertex where this particle is incoming
        self.inVertex = None
        # Barcode of vertex that has this particle as an outgoing particle
        # Ditto note about inVertexBarcode
        self.outVertexBarcode = outVertexBarcode
        # Reference to GenVertex where this particle is outgoing
        self.outVertex = None

    def __str__(self):
        pprint(vars(self))

    def __repr__(self):
        return "EA: %s" % self.particle.barcode

    def setInVertex(self, v):
        """Set particle's inVertex to be v"""
        self.inVertex = v
        self.inVertexBarcode = v.barcode
        v.inParticles.append(self.particle)

    def setOutVertex(self, v):
        """Set particle's outVertex to be v"""
        self.outVertex = v
        self.outVertexBarcode = v.barcode
        v.outParticles.append(self.particle)
        v.numOutgoing += 1


class DisplayAttributes(object):
    """Class to store attributes about visual node/edge representation
    of a particle, e.g. node shape, color"""

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
        elif self.particle.isFinalState:
            self.attr["color"] = CONFIG.final_color

        # Set interesting or not
        if interestingList:
            for i in interestingList:
                if any(x in (self.particle.name, self.particle.pdgid) for x in i[1]):
                    self.isInteresting = True
                    self.attr["color"] = i[0]

        # Set label
        if self.rawNames:
            self.attr["label"] = "%s: %s" % (self.particle.barcode,
                                             self.particle.name)
        else:
            self.attr["label"] = "%s: %s" % (self.particle.barcode,
                                             self.particle.texname)
            self.attr["texlbl"] = "$%s: %s$" % (self.particle.barcode,
                                                self.particle.texname)

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

        # TikZ options for various particles
        if not self.rawNames:
            # Color label same as edge, and puts label on tangent to curve
            # Only works if dot2tex used with --tikzedgelabels option
            self.attr["exstyle"] = "sloped,above,pos=0.6"
            self.attr["label"] = " "  # do tex names via texlbl - space is VITAL
            if abs(self.particle.pdgid) == 21:  # gluons
                self.styleGluons()
            elif abs(self.particle.pdgid) == 22:  # photons
                self.stylePhotons()
            elif abs(self.particle.pdgid) in [23, 24]:  # gauge boson
                self.styleGaugeBosons()
            elif abs(self.particle.pdgid) in range(25, 38):  # higgs bosons
                self.styleHiggs()

        # TODO: only interesting? final? or none? potentially hard to read
        # dot2tex doesn't use fontcolor anyway - bug
        # if self.isInteresting:
        #     self.attr["fontcolor"] = self.attr["color"]

    def stylePhotons(self):
        """Apply TikZ styling for photons edges - wavy, no labels"""
        self.attr["style"] = "decorate,decoration={snake,post length=5bp}"
        self.attr["texlbl"] = ""  # turn off photon labels
        self.attr["exstyle"] = ""

    def styleGaugeBosons(self):
        """Apply TikZ styling for gauge boson edges - wavy"""
        self.attr["style"] = "decorate,decoration={snake,post length=5bp}"

    def styleGluons(self):
        """Apply TikZ styling for gluon edges - spirals, no labels"""
        # self.attr["style"] = \
        # "thin, decorate,decoration={coil,amplitude=3bp,segment length=4bp}"
        # self.attr["style"] = "decorate,decoration={snake,post length=5bp}"
        # self.attr["style"] = "gluon"
        self.attr["color"] = "gray,semitransparent"
        self.attr["texlbl"] = ""  # turn off gluon labels
        self.attr["exstyle"] = ""

    def styleHiggs(self):
        """Apply TikZ styling for Higgs boson edges - dashed"""
        self.attr["style"] = "dashed"

    def generate_string(self, attributes):
        """Function to generate string with all necessary attributes.
        attributes is a list of options (i.e. dictionary keys)
        the user wants to include."""
        attr_string = ""
        for a in attributes:
            if a in self.attr.keys():
                attr_string += ''.join([a, "=\"", str(self.attr[a]), "\""])
                if a != attributes[-1]:
                    attr_string += ", "
            else:
                print "Attribute %s not in the DisplayAttributes object" % a
                continue
        return "["+attr_string+"]"

    def getNodeString(self):
        """Returns string that can be used in GraphViz to describe the node"""
        return self.generate_string(["label",
                                     "shape",
                                     "style",
                                     "fillcolor"
        ])

    def getEdgeString(self):
        """Returns string that can be used in GraphViz to describe the edge"""
        if self.rawNames:
            return self.generate_string(["label",
                                         "color",
                                         "penwidth",
                                         "arrowsize"
            ])
        else:
            return self.generate_string(["label",
                                         "texlbl",
                                         "color",
                                         "fontcolor",
                                         "arrowsize",
                                         "style",
                                         "exstyle"
            ])