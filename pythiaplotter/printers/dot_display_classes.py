"""Classes to describe visual attributes. Used when making the Graphviz file.

Also set particle label in here, see ``get_particle_label()``. Or should this be a
method for the particle?

TODO: there's so much common between the two classes, surely it must be
possible to simplify things...
"""


from __future__ import absolute_import
import logging
import pythiaplotter.utils.logging_config  # NOQA
from pythiaplotter.utils.pdgid_converter import pdgid_to_string
from .dot_config import DOT_PARTICLE_OPTS, DOT_GRAPH_OPTS


log = logging.getLogger(__name__)


def get_particle_label(particle, fancy):
    """Return string for particle label to be displayed on graph.

    Parameters
    ----------
    particle : Particle
        Particle under consideration
    fancy : bool
        If True, will use HTML/unicode in labels

    Returns
    -------
    str
        Particle label string
    """
    if fancy:
        label = r"<{0}: {1},  p<SUB>T</SUB>: {2:.2f}<br/>&eta;: {3:.2f},  &phi;: {4:.2f}>".format(
            particle.barcode, pdgid_to_string(particle.pdgid),
            float(particle.__dict__.get('pt', 0)), float(particle.__dict__.get('eta', 0)),
            float(particle.__dict__.get('phi', 0)))
        label = label.replace("inf", "&#x221e;")
        return label
    else:
        return '"{0}: {1}, pT: {2:.2f}, eta: {3:.2f}, phi: {4:.2f}"'.format(
            particle.barcode, pdgid_to_string(particle.pdgid),
            float(particle.__dict__.get('pt', 0)), float(particle.__dict__.get('eta', 0)),
            float(particle.__dict__.get('phi', 0)))


class DotEdgeAttr(object):

    def __init__(self, edge, fancy=False):
        """Hold display attributes for edge in dot graph.

        Parameters
        ----------
        edge : dict
            Edge under consideration.
        fancy : bool
            If True, will use HTML/unicode in labels
        """
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in list(edge.keys()):  # edge represents a particle
            self.add_particle_attr(edge, fancy)
        else:
            self.add_line_attr(edge)

    def __repr__(self):
        return "DotEdgeAttrRepr"

    def __str__(self):
        """Print edge attributes in dot-friendly format"""
        attr_list = ['{0}={1}'.format(*it) for it in self.attr.items()]
        return "[{0}]".format(", ".join(attr_list)) if attr_list else ""

    def add_line_attr(self, edge):
        """Simple line to represent relationship between particles"""
        pass

    def add_particle_attr(self, edge, fancy):
        """Style line as particle.

        Parameters
        ----------
        edge : dict
            Edge containing a particle
        fancy : bool
            Use HTML/unicode in labels
        """
        particle = edge["particle"]

        # Displayed edge label
        self.attr["label"] = get_particle_label(particle, fancy)

        for opt in DOT_PARTICLE_OPTS:
            if opt.filter(particle):
                self.attr.update(opt.attr['edge'])
                break


class DotNodeAttr(object):

    def __init__(self, node, fancy=False):
        """Hold display attributes for node in dot graph.

        Parameters
        ----------
        node : dict
            Node under consideration
        fancy : bool, optional
            Use HTML/unicode in labels
        """
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in list(node.keys()):  # node represents a particle
            self.add_particle_attr(node, fancy)
        else:
            self.add_point_attr(node)

    def __repr__(self):
        return "DotNodeAttrRepr"

    def __str__(self):
        """Print node attributes in dot-friendly format"""
        attr_list = ['{0}={1}'.format(*it) for it in self.attr.items()]
        return "[{0}]".format(", ".join(attr_list))

    def add_point_attr(self, node, show_barcode=False):
        """Simple point to show intersection of particles in EDGE representation.

        Parameters
        ----------
        node : dict
            ???
        show_barcode : bool, optional
            Shows the node/vertex barcode, for debugging purposes.
        """
        self.attr["shape"] = "circle" if show_barcode else "point"

    def add_particle_attr(self, node, fancy):
        """Style node as particle.

        Parameters
        ----------
        node : dict
            Node containing a Particle
        fancy : bool, optional
            Use HTML/unicode in labels
        """
        particle = node["particle"]

        # Displayed node label
        self.attr["label"] = get_particle_label(particle, fancy)

        for opt in DOT_PARTICLE_OPTS:
            if opt.filter(particle):
                self.attr.update(opt.attr['node'])
                break


class DotGraphAttr(object):
    """Hold Graphviz attributes for the graph as whole."""

    def __init__(self, graph):
        self.graph = graph
        self.attr = DOT_GRAPH_OPTS

    def __repr__(self):
        attr_list = ['{0}="{1}"'.format(*it) for it in self.attr.items()]
        return "DotGraphAttr(attr=dict({0}))".format(", ".join(attr_list))

    def __str__(self):
        """Print graph attributes in dot-friendly format"""
        attr_list = ['{0}="{1}";'.format(*it) for it in self.attr.items()]
        return "\t{0}".format("\n\t".join(attr_list))
