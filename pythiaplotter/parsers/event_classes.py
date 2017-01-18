"""
Classes to describe event & physical particles, along with helper classes to
hold Particles in graph, and four-vectors.
"""

from __future__ import division
import pythiaplotter.utils.logging_config  # NOQA
import logging
import math


log = logging.getLogger(__name__)


class Event(object):
    """Hold event info"""

    def __init__(self, event_num=0, run_num=0, lumi_section=0, label="",
                 signal_process_vtx_id=0):
        self.event_num = int(event_num)
        self.run_num = int(run_num)
        self.lumi_section = int(lumi_section)
        self.label = label
        self.graph = None  # to hold NetworkX graph
        self._particles = None

    def __repr__(self):
        ignore = ["graph", "_particles", "particles"]
        args_str = ["%s=%s" % (a, self.__dict__[a]) for a in
                    self.__dict__ if a not in ignore]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(args_str))

    def __str__(self):
        """Print event info in format suitable for use on graph or printout"""
        ignore = ["graph", "_particles", "particles"]
        info = [k + ": " + str(v) + "\n" for k, v in self.__dict__.iteritems()
                if k not in ignore]
        return "Event:\n{0}".format("".join(info))

    @property
    def particles(self):
        return self._particles

    @particles.setter
    def particles(self, particles):
        self._particles = particles
        for p in self._particles:
            p.event = self

    def print_stats(self):
        """Print some basic statistics about the event"""
        print "{0} particles in the event".format(len(self._particles))


class Particle(object):
    """Representation of a physical particle.

    Each Particle object should have a unique integer barcode,
    to uniquely identify it in an event. 0 should be used for the initial
    "system" or such like.
    """

    def __init__(self, barcode=-1, pdgid=0,
                 px=0.0, py=0.0, pz=0.0, et=0.0, pt=0.0, eta=0.0, phi=0.0,
                 energy=0.0, mass=0.0, status=0):
        self.barcode = int(barcode)  # barcode - should be a unique **number**
        self.pdgid = int(pdgid)  # PDGID - see section 43 (?) in PDGID
        self.four_mom = FourMomentum(px=px, py=py, pz=pz, et=et,
                                     pt=pt, eta=eta, energy=energy, mass=mass)
        self.status = int(status)  # status code NB diff for Pythia, hepmc, etc
        self.final_state = False
        self.initial_state = False
        self.event = None  # parent event

    def __repr__(self):
        args_str = ["%s=%s" % (k, v) for k, v in self.__dict__.items()
                    if k not in ['event', 'px', 'py', 'pz', 'energy', 'mass',
                                 'pt', 'eta', 'phi', 'status', "et"]]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(args_str))

    def __str__(self):
        # Properties to print out - we don't want all of them!
        return "Particle {0}, PDGID {1}, {2}".format(self.barcode, self.pdgid, self.four_mom)

    def __eq__(self, other):
        return self.barcode == other.barcode and self.pdgid == other.pdgid

    @property
    def px(self):
        return self.four_mom._px

    @property
    def py(self):
        return self.four_mom._py

    @property
    def pz(self):
        return self.four_mom._pz

    @property
    def pt(self):
        return self.four_mom.pt

    @property
    def eta(self):
        return self.four_mom.eta

    @property
    def phi(self):
        return self.four_mom.phi


class FourMomentum(object):
    """Class to represent a 4-vector of energy-momentum

    Conversion from px, py, pz to pt, eta, phi
    px = pt * cos(phi)
    py = pt * sin(phi)
    pz = pt * sinh (eta)

    Where:
    eta is the pseudorapidity, = -ln(tanh(theta/2))
    phi is the angle of the 3-momentum in the x-y plane relative to the x axis
    theta is the angle of the 3-momentum in the x-z plane relative to the z axis

    """

    def __init__(self, px=0.0, py=0.0, pz=0.0, et=0.0,
                 energy=0.0, mass=0.0, pt=0.0, eta=0.0, phi=0.0):
        self._px = float(px)
        self._py = float(py)
        self._pz = float(pz)
        self._pt = float(pt)
        self._eta = float(eta)
        self._phi = float(phi)
        self._energy = float(energy)
        self._et = float(et)
        self._mass = float(mass)

    def __repr__(self):
        args_str = ["%s=%s" % (k, v) for k, v in self.__dict__.items()]
        return "{0}({1})".format(self.__class__.__name__, ", ".join(args_str))

    @property
    def pt(self):
        """Return the transverse momentum.

        Defined as pt = sqrt(px^2 + py^2)
        """
        return math.hypot(self._px, self._py)

    @property
    def phi(self):
        """Return the azimuthal angle.

        phi = 0: along x axis
        phi = pi/2: along y axis

        Ensures that -pi < phi < pi
        """
        phi = math.atan(self._py / self._px) if self._px != 0 else math.pi / 2.0
        return phi

    @property
    def eta(self):
        """Return the pseudorapidity.

        Formally, eta = -ln(tanh(theta/2)).
        Here it is calculated using pz = pt * sinh(eta)

        Note that if pt == 0, eta = sign(pz) * infinity.
        """
        if self.pt == 0:
            return math.copysign(float('inf'), self._pz)
        else:
            return math.asinh(self._pz / self.pt)


class NodeParticle(object):
    """Class to hold info when particle is represented by a node.

    This contains the physical Particle object, and associated info that
    is node-specific, such as parent node and children node codes.

    parent1 and parent2 barcodes mark the edge of the range of barcodes
    of parent particles.
    """

    def __init__(self, particle, parent1_barcode, parent2_barcode):
        parent1_barcode = int(parent1_barcode)
        parent2_barcode = int(parent2_barcode)
        self.particle = particle
        self.parent1_code = parent1_barcode  # barcode range for parents
        self.parent2_code = (parent2_barcode if parent2_barcode >= parent1_barcode
                             else parent1_barcode)
        # to store barcodes of parents:
        self.parent_codes = range(parent1_barcode, parent2_barcode + 1)

    def __repr__(self):
        ignore = ["parent_codes"]
        args_str = ["%s=%r" % (a, self.__dict__[a]) for a in
                    self.__dict__ if a not in ignore]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(args_str))

    @property
    def barcode(self):
        return self.particle.barcode


class EdgeParticle(object):
    """Class to hold info when particle is represented by an edge.

    This contains the physical Particle object, and associated info that
    is edge-specific, such as incoming/outgoing vertex barcodes.

    Vertex barcodes are ints.
    """

    def __init__(self, particle, vtx_in_barcode, vtx_out_barcode):
        self.particle = particle
        self.vtx_in_barcode = int(vtx_in_barcode)
        self.vtx_out_barcode = int(vtx_out_barcode)

    @property
    def barcode(self):
        return self.particle.barcode

    def __repr__(self):
        return "{0}(barcode={1}, " \
               "vtx_in_barcode={2[vtx_in_barcode]}, " \
               "vtx_out_barcode={2[vtx_out_barcode]}," \
               "particle={2[particle]})\n".format(self.__class__.__name__,
                                                  self.barcode, self.__dict__)
