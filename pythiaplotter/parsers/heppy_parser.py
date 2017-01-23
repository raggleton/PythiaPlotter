"""Handle parsing of Heppy ROOT input files.

These must be made with both the GeneratorRelationshipAnalyzer and GeneratorAnalyzer modules,
the former adding in mother/daughter relationships, and the latter storing all gen particles.

Default is NODE representation.

See example/example_heppy.root for example input file.
"""


from __future__ import absolute_import
from contextlib import contextmanager
from itertools import chain
import logging
import pythiaplotter.utils.logging_config  # NOQA
try:
    from itertools import izip
except ImportError:
    izip = zip
import pythiaplotter.graphers.node_grapher as node_grapher
from pythiaplotter.utils.common import generate_repr_str
import ROOT
from .event_classes import Event, Particle, NodeParticle


ROOT.PyConfig.IgnoreCommandLineOptions = True  # stop stealing sys.argv
ROOT.gErrorIgnoreLevel = 1  # turn off the printing output
ROOT.gROOT.SetBatch(1)


log = logging.getLogger(__name__)


class HeppyParser(object):
    """Main class to parse Heppy ROOT file."""

    def __init__(self, filename, event_num=0, remove_redundants=False):
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
        self.event_num = event_num  # 0 = first event, etc
        self.remove_redundants = remove_redundants
        self.collection_name = "allGenPart"

    def __repr__(self):
        return generate_repr_str(self, ignore=['events'])

    def __str__(self):
        return "HeppyParser: {0}".format(self.filename)

    def parse(self):
        """Parse contents of the input file, extract particles, and assign to a NetworkX graph.

        Returns
        -------
        Event
            Event object, which contains info about the event, a list of Particles in the event,
            and a NetworkX graph object with particles assigned to nodes.
        """

        log.info("Opening event file %s" % self.filename)
        with root_open(self.filename) as f:
            tree = f.tree
            if not tree:
                raise IOError("Cannot get tree from {}".format(self.filename))

            tree.SetBranchStatus("*", 0)  # To speedup reading the Tree

            # TODO: Need to make branch names configurable somehow...
            particle_fields = ["charge", "status", "pdgId", "pt", "eta", "phi", "mass"]

            particle_branch_names = ["_".join([self.collection_name, bn])
                                     for bn in particle_fields]

            # TODO: make these configurable, somehow
            relationship_fields = ['motherIndices', 'daughterIndices']

            for bn in chain(particle_branch_names, relationship_fields):
                tree.SetBranchStatus(bn, 1)

            num_entries = tree.GetEntries()
            log.debug('%d entries in tree', num_entries)

            get_entry(tree, self.event_num)

            # need to convert from ROOT.PyIntBuffer to list manually
            mother_indices, daughter_indices = [list(tree.__getattr__(bn))
                                                for bn in relationship_fields]
            log.debug('Mother indices: %s', mother_indices)
            log.debug('Daugher indices: %s', daughter_indices)

            # Make a dict, such that a key of daughter's index returns all mother indices
            mother_map = dict()
            for daughter in set(daughter_indices):
                mother_map[daughter] = sorted([m for m, d
                                               in izip(mother_indices, daughter_indices)
                                               if d == daughter])
            log.debug('Daughter/mothers mapping: %s', mother_map)

            particle_branches = [tree.__getattr__(bn) for bn in particle_branch_names]

            node_particles = []

            for ind, entry in enumerate(izip(*particle_branches)):
                entry_map = {k: v for k, v in izip(particle_fields, entry)}
                p = Particle(barcode=ind,
                             pdgid=int(entry_map['pdgId']),
                             status=int(entry_map['status']),
                             pt=float(entry_map['pt']),
                             eta=float(entry_map['eta']),
                             phi=float(entry_map['phi']),
                             mass=float(entry_map['mass']))
                np = NodeParticle(p, 0, 0)  # we don't care about parent1/2 barcodes
                np.parent_codes = mother_map.get(ind, [])

                log.debug(np)

                node_particles.append(np)

            event = Event()
            event.particles = [np.particle for np in node_particles]
            event.graph = node_grapher.assign_particles_nodes(node_particles=node_particles,
                                                              remove_redundants=self.remove_redundants)
            return event


@contextmanager
def root_open(path, mode="READ"):
    """Context manager for opening ROOT files

    Parameters
    ----------
    path : str
        ROOT filename
    mode : str, optional
        Opening mode, READ by default

    Returns
    -------
    ROOT.TFile
        The TFile
    """
    the_file = ROOT.TFile(path, mode)
    yield the_file
    the_file.Close()


def get_entry(tree, entry_num):
    """Get entry `entry_num` in TTree.

    Parameters
    ----------
    tree : ROOT.TTree
        Description
    entry_num : int
        Description

    Returns
    -------
    int
        Number of bytes in entry

    Raises
    ------
    RuntimeError
        If cannot get entry, either because it doesn't exist, or fail for some other reason.
    """
    nbytes = tree.GetEntry(entry_num)
    if nbytes == 0:
        raise IOError("Cannot get entry {}, "
                      "tree only has {} entries".format(entry_num, tree.GetEntries()))
    elif nbytes == -1:
        raise IOError("Error getting entry {}".format(entry_num))
    return nbytes
