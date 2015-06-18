"""
Classes to describe event & physical particles
"""

import utils.logging_config
import logging


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
        args_str = ["%s=%s" % (a, self.__dict__[a]) for a in
                    self.__dict__ if a not in ["graph", "_particles", "particles"]]
        return "%s.%s(%s)" % (self.__module__, self.__class__.__name__,
                              ", ".join(args_str))

    def __str__(self):
        """Print event info in format suitable for use on graph or printout"""
        ignore = ["graph", "_particles", "particles"]
        info = [k+": "+str(v)+"\n" for k, v in self.__dict__.iteritems()
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


class Particle(object):
    """Representation of a physical particle.

    Each Particle object should have a unique integer barcode,
    to uniquely identify it in an event. 0 should be used for the initial
    "system" or such like.
    """

    def __init__(self, barcode=-1, pdgid=0, px=0.0, py=0.0, pz=0.0,
                 energy=0.0, mass=0.0, status=0, parent1=-1, parent2=-1):
        self.barcode = int(barcode)  # barcode - should be a unique **number**
        self.pdgid = int(pdgid)  # PDGID - see section 43 (?) in PDGID
        self.px = float(px)  # Store as TLorentzVector?
        self.py = float(py)
        self.pz = float(pz)
        self.pt = 0.0  # FIXME
        self.energy = float(energy)
        self.et = 0.0  # FIXME
        self.mass = float(mass)
        self.status = int(status)  # status code NB diff for Pythia, hepmc, etc
        # self.parent1_code = int(parent1)  # barcode range for parents
        # self.parent2_code = int(parent2)
        # to store barcodes of parents:
        # self.parent_codes = range(self.parent1_code, self.parent2_code + 1)
        # self.child_codes = None  # to store barcodes of children
        # self.skip = False  # Skip when writing to file
        self.final_state = False
        self.initial_state = False
        # self.parent1_code == self.parent2_code == 0
        self.event = None  # parent event
        # self.vtx_in_barcode = 0
        # self.vtx_out_barcode = 0

    def __repr__(self):
        args_str = ["%s=%s" % (k, v) for k, v in self.__dict__.items()
                    if k not in ["event"]]
        return "%s.%s(%s)" % (self.__module__, self.__class__.__name__,
                              ", ".join(args_str))

    def __str__(self):
        # Properties to print out - we don't want all of them!
        return "Particle {0}, PDGID {1}".format(self.barcode, self.pdgid)

    def __eq__(self, other):
        return self.barcode == other.barcode and self.pdgid == other.pdgid


class NodeParticle(object):
    """Class to hold info when particle is represented by a node.

    This contains the physical Particle object, and associated info that
    is node-specific, such as parent node and children node codes.

    Why do we store the barcode and not a reference to the parent particle?
    This is becasue programs that output in node representation list
    parents using their particle ID in the event (here, barcode). Thus, when
    constructing the NodeParticle, we need the barcode, not the object itself.
    In addition, we can then infer all the parent barcodes based on the parent1
    and parent2 barcodes, which mark the edge of the range of barcodes of parent
    particles.
    """

    def __init__(self, particle, parent1_barcode, parent2_barcode):
        parent1_barcode = int(parent1_barcode)
        parent2_barcode = int(parent2_barcode)
        self.particle = particle
        self.parent1_code = parent1_barcode  # barcode range for parents
        self.parent2_code = parent2_barcode
        # to store barcodes of parents:
        self.parent_codes = range(parent1_barcode, parent2_barcode + 1)
        # self.child_codes = []  # to store barcodes of children
        self.particle.initial_state = parent1_barcode == parent2_barcode == 0

    def __repr__(self):
        ignore = ["particle", "child_codes"]
        args_str = ["%s=%s" % (a, self.__dict__[a]) for a in
                    self.__dict__ if a not in ignore]
        return "%s.%s(%s)" % (self.__module__, self.__class__.__name__,
                              ", ".join(args_str))

    @property
    def barcode(self):
        return self.particle.barcode


class EdgeParticle(object):
    """Class to hold info when particle is represented by an edge.

    This contains the physical Particle object, and associated info that
    is edge-specific, such as incoming/outgoing vertex barcodes.
    """

    def __init__(self, particle, vtx_in_barcode, vtx_out_barcode):
        self.particle = particle
        self.vtx_in_barcode = vtx_in_barcode
        self.vtx_out_barcode = vtx_out_barcode

    @property
    def barcode(self):
        return self.particle.barcode

    def __repr__(self):
        return "{0}(barcode={1}, " \
               "vtx_in_barcode={2[vtx_in_barcode]}, " \
               "vtx_out_barcode={2[vtx_out_barcode]})\n".format(
            self.__class__.__name__,
            self.barcode,
            self.__dict__)
