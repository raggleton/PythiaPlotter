"""Handle parsing of Heppy ROOT input files.

These must be made with the GeneratorRelationshipAnalyzer modules,
adding in mother/daughter relationships, and storing all gen particles.

Default is NODE representation.

See example/example_heppy.root for example input file.
"""


from __future__ import absolute_import
from contextlib import contextmanager
from itertools import chain
try:
    from itertools import izip
except ImportError:
    izip = zip
import ROOT  # pylint: disable=import-error
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str
from .event_classes import Event, Particle, NodeParticle


ROOT.PyConfig.IgnoreCommandLineOptions = True  # stop stealing sys.argv
ROOT.gErrorIgnoreLevel = 1  # turn off the printing output
ROOT.gROOT.SetBatch(1)


log = get_logger(__name__)


class HeppyParser(object):
    """Main class to parse Heppy ROOT file."""

    def __init__(self, filename, event_num=0,
                 particle_collection_name="allGenPart",
                 mother_index_branch_name="motherIndices",
                 daughter_index_branch_name="daughterIndices"):
        """
        Parameters
        ----------
        filename : str
            Input filename.
        event_num : int, optional
            Index of event to parse in input file. (0 = first event)
        particle_collection_name : str
            Stem for the gen particle collection. e.g. if pt stored in `allGenPart_pt`,
            this should be `allGenPart`
        mother_index_branch_name : str
            Name of branch with mother indices
        daughter_index_branch_name : str
            Name of branch with daughter indices
        """
        self.filename = filename
        self.event_num = event_num  # 0 = first event, etc
        self.particle_collection_name = particle_collection_name
        self.mother_index_branch_name = mother_index_branch_name
        self.daughter_index_branch_name = daughter_index_branch_name

    def __repr__(self):
        return generate_repr_str(self, ignore=['events'])

    def __str__(self):
        return "HeppyParser: {0}".format(self.filename)

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
        with root_open(self.filename) as f:
            tree = f.tree
            if not tree:
                raise IOError("Cannot get tree from {}".format(self.filename))

            tree.SetBranchStatus("*", 0)  # To speedup reading the Tree

            particle_fields = ["charge", "status", "pdgId", "pt", "eta", "phi", "mass"]

            particle_branch_names = ["_".join([self.particle_collection_name, bn])
                                     for bn in particle_fields]

            relationship_fields = [self.mother_index_branch_name, self.daughter_index_branch_name]

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
                contents_dict = {k: v for k, v in izip(particle_fields, entry)}
                p = Particle(barcode=ind,
                             pdgid=int(contents_dict['pdgId']),
                             status=int(contents_dict['status']),
                             pt=float(contents_dict['pt']),
                             eta=float(contents_dict['eta']),
                             phi=float(contents_dict['phi']),
                             mass=float(contents_dict['mass']))
                np = NodeParticle(p, parent_barcodes=mother_map.get(ind, []))

                # Kill the load of final-state particles who are children of an
                # incoming proton, heppy like to produce loads of these
                parent_particles = [n for n in node_particles
                                    if n.barcode in np.parent_barcodes]
                if (p.status == 1 and len(parent_particles) == 1 and
                    parent_particles[0].barcode in [0, 1]):
                    continue

                log.debug(np)

                node_particles.append(np)

            event = Event(event_num=self.event_num, source=self.filename)
            return event, node_particles


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
