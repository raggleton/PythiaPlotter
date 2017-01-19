"""
Handle parsing of standalone Pythia 8 screen output.

Default is NODE representation for particles.
See example/example_pythia8.txt for example input file.

TODO: reshuffle blocks - non optimal spreading out atm
"""


from __future__ import absolute_import
import pythiaplotter.utils.logging_config  # NOQA
import logging
try:
    from itertools import izip
except ImportError:
    izip = zip
from pprint import pformat
from .event_classes import Event, Particle, NodeParticle
import pythiaplotter.graphers.node_grapher as node_grapher
from pythiaplotter.utils.common import map_columns


log = logging.getLogger(__name__)


class PythiaBlock(object):
    """Represent a 'block' in Pythia output e.g. Event Listing"""

    def __init__(self, name, contents=None, parser=None):
        self.name = name
        self.contents = contents if contents else []
        self.parser = parser  # method to parser contents
        self.parser_results = None  # to hold output from self.parser

    def __repr__(self):
        return "%s(%r, parser=%s, contents=%s)" % (self.__class__.__name__,
                                                   self.name,
                                                   self.parser,
                                                   self.contents)

    def __str__(self):
        return "%s:\n%s" % (self.name, '\n'.join(self.contents))

    def parse_block(self):
        """Run the instance parser over contents."""
        log.debug("Parsing block %s" % self.name)
        self.parser_results = self.parser(self.contents)


def parse_event_block(contents):
    """
    Parses Event Listing block in Pythia output
    """
    # These indicate non-particle lines - matches words
    ignore = (("no", "id"), ("Charge", "sum:"), ("0", "90", "(system)"))

    # Store all the NodeParticles in the event
    node_particles = []

    for line in contents:
        log.debug(line)

        # first determine if interesting line or not - checks to see if entries
        # in ignore tuple match entries in parts list
        if sum([all([i == p for i, p in izip(ig, line.split())]) for ig in ignore]):
            continue

        # Now assign each field to a dict to make life easier
        fields = ["barcode", "pdgid", "name", "status", "parent1", "parent2",
                  "child1", "child2", "colours1", "colours2",
                  "px", "py", "pz", "energy", "mass"]
        contents_dict = map_columns_to_dict(fields, line)
        log.debug(contents_dict)
        # Create a Particle obj and add to total
        p = Particle(barcode=contents_dict['barcode'],
                     pdgid=contents_dict['pdgid'],
                     status=contents_dict['status'],
                     px=contents_dict['px'],
                     py=contents_dict['py'],
                     pz=contents_dict['pz'],
                     energy=contents_dict['energy'],
                     mass=contents_dict['mass'])
        # Sometimes parent2 = 0, so set = parent1 if this is the case
        np = NodeParticle(particle=p,
                          parent1_barcode=contents_dict['parent1'],
                          parent2_barcode=(contents_dict['parent2']
                                           if int(contents_dict['parent2'])
                                           else contents_dict['parent1']))
        node_particles.append(np)

    return node_particles


def parse_info_block(contents):
    """Method to parse Info block. Makes Event object to hold particles"""
    return Event()


def parse_stats_block(contents):
    """Method to parse Statistics block. Kept unimplemented."""
    pass


class Pythia8Parser(object):
    """Main class to parse Pythia 8 screen output from a text file."""

    # Block types in Pythia output
    # For each, we store:
    # strings that indicate start/end or block;
    # the start/end indices of any blocks;
    # a list of individual block contents;
    # and the parser method to handle this type of block
    info_start = "PYTHIA Info Listing"
    info_end = "End PYTHIA Info Listing"
    info_blocks = dict(str_start=info_start, str_end=info_end,
                       ind_start=[], ind_end=[], blocks=[],
                       parser=parse_info_block)

    full_evt_start = "PYTHIA Event Listing  (complete event)"
    full_evt_end = "End PYTHIA Event Listing"
    full_evt_blocks = dict(str_start=full_evt_start, str_end=full_evt_end,
                           ind_start=[], ind_end=[], blocks=[],
                           parser=parse_event_block)

    hard_evt_start = "PYTHIA Event Listing  (hard process)"
    hard_evt_end = "End PYTHIA Event Listing"
    hard_evt_blocks = dict(str_start=hard_evt_start, str_end=hard_evt_end,
                           ind_start=[], ind_end=[], blocks=[],
                           parser=parse_event_block)

    stats_start = "PYTHIA Event and Cross Section Statistics"
    stats_end = "End PYTHIA Event and Cross Section Statistics"
    stats_blocks = dict(str_start=stats_start, str_end=stats_end,
                        ind_start=[], ind_end=[], blocks=[],
                        parser=parse_stats_block)

    # All the different blocks we want to be able to parse, with sensible names
    block_types = dict(FullEvent=full_evt_blocks,
                       Info=info_blocks,
                       HardEvent=hard_evt_blocks)

    def __init__(self, filename, event_num=0, remove_redundants=True):
        self.filename = filename
        self.event_num = event_num  # 0 = first event, etc
        self.remove_redundants = remove_redundants
        log.info("Opening event file %s" % filename)

        # store file contents in list to slice up easily
        # TODO: change this - will use large amount of RAM for big files!
        self.contents = []
        with open(filename, "r") as f:
            lines = [l.replace("\n", "").strip() for l in list(f)]
            self.contents = [l for l in lines if l]

    def __repr__(self):
        return "%s(filename=%r, event_num=%d)" % (self.__class__.__name__,
                                                  self.filename,
                                                  self.event_num)

    def __str__(self):
        return "Pythia8Parser:\n%s" % pformat(self.block_types)

    def parse(self):
        """Go through contents and find blocks, then deal with them.

        Returns an Event object, which contains info about the event,
        a list of Particles in the event, and a NetworkX graph obj
        with particles assigned to nodes.
        """

        # Find all start & end indices for blocks
        for i, line in enumerate(self.contents):
            for block in self.block_types.values():
                if block["str_start"] in line:
                    block["ind_start"].append(i)
                    log.debug("Block starting line: %s" % line)
                if block["str_end"] in line:
                    # check that there's at least one ind_start < i
                    if sum([j < i for j in block["ind_start"]]):
                        block["ind_end"].append(i)
                        log.debug("Block ending line: %s" % line)

        # Now pull the contents from files & parse
        for name, block in self.block_types.items():
            for pair in izip(block["ind_start"], block["ind_end"]):
                pb = PythiaBlock(name=name, parser=block["parser"],
                                 contents=self.contents[pair[0] + 1: pair[1]])
                pb.parse_block()
                block["blocks"].append(pb)

        if len(self.block_types["FullEvent"]["blocks"]) < self.event_num:
            raise IndexError("Cannot access event number %d, no such event" % self.event_num)

        # Deal with each type
        # Info block: make a blank Event() object in case there's no Info block,
        # assigning grapher (TODO: move elsewhere?)
        event = (self.block_types["Info"]["blocks"][self.event_num].parser_results
                 if self.block_types["Info"]["blocks"] else Event())

        # Hard event blocks:
        # hard_node_particles = self.block_types["HardEvent"]["blocks"][self.event_num].parser_results

        # Full event blocks:
        full_node_particles = self.block_types["FullEvent"]["blocks"][self.event_num].parser_results

        # Assign particles to graph nodes
        event.particles = [np.particle for np in full_node_particles]
        event.graph = node_grapher.assign_particles_nodes(node_particles=full_node_particles,
                                                          remove_redundants=self.remove_redundants)

        return event
