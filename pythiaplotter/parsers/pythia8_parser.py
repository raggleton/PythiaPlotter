"""Handle parsing of standalone Pythia 8 screen output.

Default is NODE representation for particles.

See example/example_pythia8.txt for example input file.

TODO: reshuffle blocks - non optimal spreading out atm
"""


from __future__ import absolute_import
from pprint import pformat
try:
    from itertools import izip
except ImportError:
    izip = zip
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import map_columns_to_dict, generate_repr_str
from .event_classes import Event, Particle, NodeParticle


log = get_logger(__name__)


class PythiaBlock(object):

    def __init__(self, name, contents=None, parser=None):
        """Represent a 'block' in Pythia output e.g. Event Listing

        Parameters
        ----------
        name : str
            Name of the block
        contents : list[str], optional
            Block contents to be parsed
        parser : function, optional
            Function that takes `contents` as argument.

        Attributes
        ----------
        parser_results : list[object]
            Results from the parser function
        """
        self.name = name
        self.contents = contents if contents else []
        self.parser = parser  # method to parser contents
        self.parser_results = None  # to hold output from self.parser

    def __repr__(self):
        return generate_repr_str(self, ignore=['parser_results'])

    def __str__(self):
        return "%s:\n%s" % (self.name, '\n'.join(self.contents))

    def parse_block(self):
        """Run the instance parser over contents, and store results."""
        log.debug("Parsing block %s", self.name)
        self.parser_results = self.parser(self.contents)


def parse_event_block(contents):
    """Parse Event listing block in Pythia output

    Parameters
    ----------
    contents : list[str]
        Contents of event block.

    Returns
    -------
    list[NodeParticle]
        NodeParticles extracted from event, with mother barcodes set.
    """
    # These indicate non-particle lines - matches words
    ignore = (("no", "id"), ("Charge", "sum:"), ("0", "90", "(system)"))

    # Store all the NodeParticles in the event
    node_particles = []

    log.debug("start of raw contents")
    log.debug(contents)
    log.debug("end of raw contents")

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
        p = Particle(barcode=int(contents_dict['barcode']),
                     pdgid=int(contents_dict['pdgid']),
                     status=int(contents_dict['status']),
                     px=float(contents_dict['px']),
                     py=float(contents_dict['py']),
                     pz=float(contents_dict['pz']),
                     energy=float(contents_dict['energy']),
                     mass=float(contents_dict['mass']))
        # Sometimes parent2 = 0, so set = parent1 if this is the case
        if int(contents_dict['parent2']) == 0:
            contents_dict['parent2'] = contents_dict['parent1']
        np = NodeParticle(particle=p,
                          parent_barcodes=list(range(int(contents_dict['parent1']),
                                                     int(contents_dict['parent2']) + 1)))
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

    full_evt_start = "PYTHIA Event Listing  (complete event)"
    full_evt_end = "End PYTHIA Event Listing"

    hard_evt_start = "PYTHIA Event Listing  (hard process)"
    hard_evt_end = "End PYTHIA Event Listing"

    stats_start = "PYTHIA Event and Cross Section Statistics"
    stats_end = "End PYTHIA Event and Cross Section Statistics"

    def __init__(self, filename, event_num=0):
        """
        Parameters
        ----------
        filename : str
            Input filename.
        event_num : int, optional
            Index of event to parse in input file. (0 = first event)
        """
        self.filename = filename
        self.event_num = event_num

        self.info_blocks = dict(str_start=self.info_start, str_end=self.info_end,
                                ind_start=[], ind_end=[], blocks=[],
                                parser=parse_info_block)

        self.full_evt_blocks = dict(str_start=self.full_evt_start, str_end=self.full_evt_end,
                                    ind_start=[], ind_end=[], blocks=[],
                                    parser=parse_event_block)

        self.hard_evt_blocks = dict(str_start=self.hard_evt_start, str_end=self.hard_evt_end,
                                    ind_start=[], ind_end=[], blocks=[],
                                    parser=parse_event_block)

        self.stats_blocks = dict(str_start=self.stats_start, str_end=self.stats_end,
                                 ind_start=[], ind_end=[], blocks=[],
                                 parser=parse_stats_block)

        # All the different blocks we want to be able to parse, with sensible names
        self.block_types = dict(FullEvent=self.full_evt_blocks,
                                Info=self.info_blocks,
                                HardEvent=self.hard_evt_blocks)

        # store file contents in list to slice up easily
        self.contents = []

    def __repr__(self):
        return generate_repr_str(self, ignore=['contents', 'info_blocks', 'full_evt_blocks',
                                               'hard_evt_blocks', 'stats_blocks', 'block_types'])

    def __str__(self):
        return "Pythia8Parser:\n%s" % pformat(self.block_types)

    def parse(self):
        """Parse contents of the input file, extract particles, and assign to a NetworkX graph.

        Returns
        -------
        Event
            Event object containing info about the event.
        list[NodeParticle]
            Collection of NodeParticles to be assigned to a graph.
        """
        log.info("Opening event file %s", self.filename)
        with open(self.filename, "r") as f:
            lines = [l.replace("\n", "").strip() for l in list(f)]
            self.contents = [l for l in lines if l]

        # Find all start & end indices for blocks
        for i, line in enumerate(self.contents):
            for block in self.block_types.values():
                if block["str_start"] in line:
                    block["ind_start"].append(i)
                    log.debug("Block starting line: %s", line)
                if block["str_end"] in line:
                    # check that there's at least one ind_start < i
                    if sum([j < i for j in block["ind_start"]]):
                        block["ind_end"].append(i)
                        log.debug("Block ending line: %s", line)

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
        event = Event()
        if self.block_types["Info"]["blocks"]:
            event = self.block_types["Info"]["blocks"][self.event_num].parser_results

        event.event_num = self.event_num
        event.source = self.filename

        # Hard event blocks:
        # hard_node_particles = self.block_types["HardEvent"]["blocks"][self.event_num].parser_results

        # Full event blocks:
        full_node_particles = self.block_types["FullEvent"]["blocks"][self.event_num].parser_results

        return event, full_node_particles
