"""Handle parsing of HepMC files.

Default is EDGE representation.

See example/example_hepmc.hepmc for example input file.
"""


from __future__ import absolute_import, division
from pprint import pformat
import logging
import pythiaplotter.utils.logging_config  # NOQA
import pythiaplotter.graphers.edge_grapher as edge_grapher
from pythiaplotter.graphers.converters import edge_to_node
from pythiaplotter.utils.common import map_columns_to_dict, generate_repr_str
from .event_classes import Event, Particle, EdgeParticle


log = logging.getLogger(__name__)


class HepMCParser(object):
    """Main class to parse a HepMC file.

    User can pass in an event number to return the event with that ID.
    If unassigned, or no events with that event number,
    return first event in file.
    """

    def __init__(self, filename, event_num=0, remove_redundants=True):
        """
        Parameters
        ----------
        filename : str
            Input filename.
        event_num : int, optional
            Index of event to parse in input file. (0 = first event)
        remove_redundants : bool, optional
            Remove redundant particles from the graph.
        """
        self.filename = filename
        self.event_num = event_num
        self.remove_redundants = remove_redundants
        self.events = []

    def __repr__(self):
        return generate_repr_str(self, ignore=['events'])

    def __str__(self):
        return "HepMCParser:\n%s" % pformat(self.filename)

    def parse(self):
        """Parse contents of the input file, extract particles, and assign to a NetworkX graph.

        Returns
        -------
        Event
            Event object, which contains info about the event, a list of Particles in the event,
            and a NetworkX graph object with particles assigned to edges.
        """
        # Loop through file, line-by-line.
        # Once we reach an event line with the require line number, then
        # we start parsing the particle/vertex lines. Otherwise we eat up all the RAM!

        parse_event = False
        current_event = None
        current_vertex = None
        edge_particles = []
        # since HepMC can output in either MeV or GeV, but we all prefer GeV,
        # this allows conversion to GeV
        energy_multiplier = 1.

        log.info("Opening event file %s", self.filename)
        with open(self.filename) as f:
            for line in f:
                if line.startswith("E") or "END_EVENT_LISTING" in line:
                    # General GenEvent information
                    if current_event:
                        # Do only having read in all particles in an event
                        # current_event.particles = [ep.particle for ep in edge_particles]
                        current_event.particles = edge_particles
                        break

                    if line.startswith("E"):
                        current_event = self.parse_event_line(line)
                        if current_event.event_num == self.event_num:
                            parse_event = True
                        else:
                            current_event = None

                if parse_event:
                    if line.startswith("V"):
                        # GenVertex info
                        current_vertex = self.parse_vertex_line(line)
                    elif line.startswith("P"):
                        # GenParticle info
                        edge_particle = self.parse_particle_line(line)
                        edge_particle.vtx_out_barcode = current_vertex.barcode
                        log.debug(edge_particle.particle)
                        # If the particle has vtx_in_barcode = 0,
                        # then this is a 'dangling' vertex (i.e. not in the list
                        # of vertices) and we must create one instead.
                        # Use (10000*|particle.vtx_out_barcode|)+particle.barcode
                        # for a unique barcode, since we won't have 10000
                        # particles in an event.

                        def _generate_unique_id(edge_particle):
                            return 10000 * abs(edge_particle.vtx_out_barcode) + edge_particle.barcode

                        # This is a final-state particle
                        if edge_particle.vtx_in_barcode == 0:
                            edge_particle.vtx_in_barcode = _generate_unique_id(edge_particle)
                            edge_particle.particle.final_state = True

                        # If the vtx_in_barcode = vtx_out_barcode, then we have
                        # a cyclical edge. This is normally reserved for an
                        # incoming proton. Need to create a new "out" node, since
                        # other particles will be outgoing from this node
                        if edge_particle.vtx_in_barcode == edge_particle.vtx_out_barcode:
                            edge_particle.vtx_out_barcode = _generate_unique_id(edge_particle)
                            edge_particle.particle.initial_state = True

                        edge_particles.append(edge_particle)
                    if line.startswith("U"):
                        # Units info
                        energy, length = self.parse_units_line(line)
                        if energy == "MEV":
                            energy_multiplier = 1 / 1000

        if not current_event:
            raise IndexError("Cannot find an event with event number %d" % self.event_num)

        # Correct units
        for p in current_event.particles:
            for attr in ['px', 'py', 'pz', 'mass', 'energy', 'pt']:
                try:
                    val = getattr(p.particle, attr)
                    setattr(p.particle, attr, val * energy_multiplier)
                except AttributeError:
                    pass

        current_event.graph = edge_grapher.assign_particles_edges(current_event.particles,
                                                                  self.remove_redundants)
        return current_event

    def parse_event_line(self, line):
        """Parse a HepMC GenEvent line and return an Event object"""
        fields = ["event_num", "num_mpi", "scale", "aQCD", "aQED",
                  "signal_process_id", "signal_process_vtx_id", "n_vtx",
                  "beam1_pdgid", "beam2_pdgid"]
        contents = map_columns_to_dict(fields, line[1:])
        return Event(event_num=contents["event_num"],
                     signal_process_vtx_id=contents["signal_process_vtx_id"])

    def parse_vertex_line(self, line):
        """Parse a HepMC GenVertex line and return a GenVertex object"""
        fields = ["barcode", "id", "x", "y", "z", "ctau", "n_orphan_in", "n_out"]
        contents = map_columns_to_dict(fields, line[1:])
        return GenVertex(barcode=abs(int(contents["barcode"])),
                         n_orphan_in=contents["n_orphan_in"])

    def parse_particle_line(self, line):
        """Parse a HepMC GenParticle line and return an EdgeParticle object

        Note that the EdgeParticle does not have vtx_out_barcode assigned here,
        since we are parsing a line in isolation. The vtx_out_barcode is added
        in the main pars() method. We just use a dummy value for now.
        """
        fields = ["barcode", "pdgid", "px", "py", "pz", "energy", "mass",
                  "status", "pol_theta", "pol_phi", "vtx_in_barcode"]
        contents = map_columns_to_dict(fields, line[1:])
        p = Particle(barcode=int(contents["barcode"]),
                     pdgid=int(contents["pdgid"]),
                     status=contents["status"],
                     px=float(contents["px"]),
                     py=float(contents["py"]),
                     pz=float(contents["pz"]),
                     energy=float(contents["energy"]),
                     mass=float(contents["mass"]))
        log.debug(p)
        ep = EdgeParticle(particle=p,
                          vtx_in_barcode=abs(int(contents['vtx_in_barcode'])),
                          vtx_out_barcode=0)
        return ep

    def parse_units_line(self, line):
        """Parse units specification line.

        Parameters
        ----------
        line : str
            Line to parse

        Returns
        -------
        str, str
            Energy and length units
        """
        return line.split()[1:]


class GenVertex(object):
    """Helper class to represent a HepMC GenVertex object.

    Vertices have a barcode that is an integer.

    Only exists inside this parser module since it is only used for parsing
    file and when assigning particles to a NetworkX graph.

    Use a namedtuple instead?
    """

    def __init__(self, barcode, n_orphan_in=0):
        self.barcode = int(barcode)
        self.n_orphan_in = n_orphan_in

    def __repr__(self):
        return generate_repr_str(self)
