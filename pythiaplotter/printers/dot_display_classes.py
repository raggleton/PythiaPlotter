"""Classes to describe visual attributes. Used when making the Graphviz file.

Also set particle label in here, see ``get_particle_label()``. Or should this be a
method for the particle?

TODO: there's so much common between the two classes, surely it must be
possible to simplify things...
"""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.pdgid_converter import pdgid_to_string
from pythiaplotter.utils.common import generate_repr_str, check_representation_str


log = get_logger(__name__)


def validate_particle_opt(opt):
    """Validate particle options dict"""
    for key in ['filter', 'attr']:
        if key not in opt:
            raise KeyError("Key '%s' must be in particle options dict" % key)
    for key in ['node', 'edge']:
        if key not in opt['attr']:
            raise KeyError("Key '%s' must be in particle options dict['attr']" % key)


def get_particle_label(particle, representation, label_opts, fancy=True):
    """Return string for particle label to be displayed on graph.

    Parameters
    ----------
    particle : Particle
        Particle under consideration
    representation : {"NODE", "EDGE"}
        Particle representation
    label_opts : dict
        Dict of labels for different representations and fancy/plain
    fancy : bool
        If True, will use HTML/unicode in labels

    Returns
    -------
    str
        Particle label string

    Raises
    ------
    RuntimeError
        If representation is not one of "NODE", "EDGE"
    """
    check_representation_str(representation)
    style_key = "fancy" if fancy else "plain"
    label = label_opts[representation.lower()][style_key].format(**particle.__dict__)
    if fancy:
        label = label.replace("inf", "&#x221e;")
    return label


class DotEdgeAttrGenerator(object):

    def __init__(self, style_opts, label_opts):
        """Generate Graphviz attribute string for an edge.

        Parameters
        ----------
        style_opts : list[dict]
            List of style option dicts for particles, each with `filter` and `attr` fields.
        label_opts : dict
            Dict of label templates, for node/edge and fancy/plain.
        """
        self.style_opts = style_opts
        for op in self.style_opts:
            validate_particle_opt(op)
        self.label_opts = label_opts

    def __repr__(self):
        return generate_repr_str(self)

    def gv_str(self, edge, fancy):
        """Generate string from an edge. Can be used directly in Graphviz file.

        Parameters
        ----------
        edge : dict
            Edge to process
        fancy : bool
            Whether to do fancy stylings or not
        """
        attr = {}
        if "particle" in list(edge.keys()):
            particle = edge["particle"]

            # Displayed node label
            attr["label"] = get_particle_label(particle, "EDGE", self.label_opts, fancy)

            for opt in self.style_opts:
                if opt['filter'](particle):
                    attr.update(opt['attr']['edge'])
                    break

        attr_list = ['{0}={1}'.format(*it) for it in attr.items()]
        return "[{0}]".format(", ".join(attr_list))


class DotNodeAttrGenerator(object):

    def __init__(self, style_opts, label_opts):
        """Generate Graphviz attribute string for a node.

        Parameters
        ----------
        style_opts : list[dict]
            List of style option dicts for particles, each with `filter` and `attr` fields.
        label_opts : dict
            Dict of label templates, for node/edge and fancy/plain.
        """
        self.style_opts = style_opts
        for op in self.style_opts:
            validate_particle_opt(op)
        self.label_opts = label_opts

    def __repr__(self):
        return generate_repr_str(self)

    def gv_str(self, node, fancy):
        """Generate string from a node. Can be used directly in Graphviz file.

        Parameters
        ----------
        node : dict
            Node to process
        fancy : bool
            Whether to do fancy stylings or not
        """
        attr = {}
        if "particle" in list(node.keys()):
            particle = node["particle"]

            # Displayed node label
            attr["label"] = get_particle_label(particle, "NODE", self.label_opts, fancy)

            for opt in self.style_opts:
                if opt['filter'](particle):
                    attr.update(opt['attr']['node'])
                    break
        else:
            attr["shape"] = "point"

        attr_list = ['{0}={1}'.format(*it) for it in attr.items()]
        return "[{0}]".format(", ".join(attr_list))


class DotGraphAttrGenerator(object):
    """Generate Graphviz string with overall graph options"""

    def __init__(self, attr):
        self.attr = attr

    def gv_str(self):
        """Print graph attributes in dot-friendly format"""
        attr_list = ['{0}={1};'.format(*it) for it in self.attr.items()]
        return "\n".join(attr_list)
