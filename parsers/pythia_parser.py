"""
Handle parsing of Pythia 8 screen output.

TODO: reshuffle blocks - non optimal spreading out atm
"""


from itertools import izip
from pprint import pprint, pformat
from event_classes import Event, Particle
import node_grapher
import utils.user_args as user_args


class PythiaBlock(object):
    """Represent a 'block' in Pythia output e.g. Event Listing"""

    def __init__(self, name, contents=None, parser=None):
        self.name = name
        self.contents = contents if contents else []
        self.parser = parser  # method to parser contents
        self.parse_results = None  # to hold output from self.parser

    def __repr__(self):
        return "%s.%s(%r, parser=%s, contents=%s)" % (self.__module__,
                                                      self.__class__.__name__,
                                                      self.name,
                                                      self.parser,
                                                      self.contents)

    def __str__(self):
        return "%s:\n%s" % (self.name, '\n'.join(self.contents))

    def parse_block(self):
        """Run the instance parser over contents."""

        self.parse_results = self.parser(self.contents)


def parse_event_block(contents):
    """
    Parses Event Listing block in Pythia output
    """
    # These indicate non-particle lines - matches words
    ignore = (("no", "id"), ("Charge", "sum:"), ("0", "90", "(system)"))

    #  Store all particles in event
    particles = []

    for line in contents:
        parts = line.split()
        # print parts

        # first determine if interesting line or not - checks to see if entries
        # in ignore tuple match entries in parts list
        if sum([all([i == p for i, p in izip(ig, parts)]) for ig in ignore]):
            continue

        # Create a Particle obj and add to total
        # Sometimes parent2 = 0, so set = parent1
        part = Particle(barcode=parts[0],
                        pdgid=parts[1],
                        status=parts[3],
                        px=parts[10],
                        py=parts[11],
                        pz=parts[12],
                        energy=parts[13],
                        mass=parts[14],
                        parent1=parts[4],
                        parent2=parts[5] if int(parts[5]) else parts[4])

        particles.append(part)

    return particles


def parse_info_block(contents):
    """Method to parse Info block. Makes Event object to hold particles"""
    return Event()


def parse_stats_block(contents):
    """Method to parse Statistics block. Kept unimplemented."""
    pass


class PythiaParser(object):
    """Main class to parse Pythia 8 screen output from a text file.

    Returns an Event object, which contains a list of Particles, and
    a NetworkX graph obj with particles assigned to nodes.
    """

    # Block types in Pythia output
    # For each, we store: strings that indicate start/end or block;
    # the start/end indicies of any blocks; a list of individual block contents;
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
                       # Stats=stats_blocks)

    def __init__(self, filename, event_num=0, remove_redundants=True):
        self.filename = filename
        self.evt_num = event_num
        self.remove_redundants = remove_redundants
        # store file contents in list to slice up easily
        self.contents = []
        with open(filename, "r") as f:
            self.contents = filter(None, [l.replace("\n", "").strip() for l in list(f)])

    def __repr__(self):
        return "%s.%s(filename=%r, event_num=%d)" % (self.__module__,
                                                     self.__class__.__name__,
                                                     self.filename,
                                                     self.event_num)

    def __str__(self):
        return "PythiaParser:\n%s" % pformat(self.block_types)

    def parse(self):
        """Go through contents and find blocks, then deal with them."""

        # Find all start & end indices for blocks
        for i, line in enumerate(self.contents):
            for block in self.block_types.values():
                if block["str_start"] in line:
                    block["ind_start"].append(i)
                if block["str_end"] in line:
                    # check that there's at least one ind_start < i
                    if sum([j < i for j in block["ind_start"]]):
                        block["ind_end"].append(i)

        # Now pull the contents from files & parse
        for name, block in self.block_types.items():
            for pair in izip(block["ind_start"], block["ind_end"]):
                pb = PythiaBlock(name=name, parser=block["parser"],
                                 contents=self.contents[pair[0] + 1:pair[1]])
                pb.parse_block()
                block["blocks"].append(pb)

        # Deal with each type
        # Info block: make a blank Event() object incase there's no Info block,
        # assigning grapher (TODO: move elsewhere?)
        event = (self.block_types["Info"]["blocks"][0].parse_results
                 if self.block_types["Info"]["blocks"] else Event())

        # Hard event blocks:
        hard_particles = self.block_types["HardEvent"]["blocks"][self.evt_num].parse_results

        # Full event blocks:
        full_particles = self.block_types["FullEvent"]["blocks"][self.evt_num].parse_results

        # Assign particles to graph nodes
        event.particles = full_particles
        event.graph = node_grapher.assign_particles_nodes(event.particles, self.remove_redundants)

        # TODO: use user args
        # if user_args.args.verbose:
        # pprint(event)
        # pprint(event.graph.node)

        return event
