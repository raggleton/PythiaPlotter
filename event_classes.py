"""
Classes to describe event & particles
"""


class Event(object):
    """Hold event info"""

    def __init__(self, event_num=0, run_num=0, lumi_section=0):
        self.event_num = int(event_num)
        self.run_num = int(run_num)
        self.lumi_section = int(lumi_section)
        self.graph = None  # to hold NetworkX graph

    def __repr__(self):
        return "STUFF HERE"

    def __str__(self):
        return "STUFF HERE"

    @particles.setter
    def particles(self, particles):
        self.particles = particles
        for p in self.particles:
            p.event = self


class Particle(object):
    """Representation of a particle

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
        self.status = int(status)  # status code, diff for Pythia & hepmc
        self.parent1_code = int(parent1) # barcode range for parents
        self.parent2_code = int(parent2)
        self.parent_codes = range(self.parent1_code, self.parent2_code+1) # to store barcodes of parents
        self.child_codes = None # to store barcodes of children
        # self.name = convert.pdgid_to_string(self.pdgid)  # raw form e.g pi0
        # self.texname = convert.pdgid_to_tex(self.pdgid)  # tex e.g \pi^0
        # self.skip = False  # Skip when writing to file
        # self.final_state = False
        self.initial_state = self.parent1_code == self.parent2_code == 0
        self.event = None  # parent event

    def __repr__(self):
        args_str = []
        for k, v in self.__dict__.items():
            args_str.append("%s=%s" % (k, v))

        return "%s.%s(%s)" % (self.__module__, self.__class__.__name__,
                             ", ".join(args_str))

    def __str__(self):
        # Properties to print out - we don't want all of them!
        properties = dict(
                          # skip=self.skip,
                          # intital_state=self.initial_state,
                          # final_state=self.final_state
                          m1=self.parent1_code,
                          m2=self.parent2_code
                          )
        return "Particle %s, PDGID %d, %s" % (self.barcode, self.pdgid, str(properties))

    def __eq__(self, other):
        return self.barcode == other.barcode and self.pdgid == other.pdgid