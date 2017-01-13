"""
Classes to describe visual attributes. Used when making Graphviz file.

Also set particle label in here, see get_particle_label(). Or should this be a
method for the particle?

TODO: there's so much common between the two classes, surely it must be
possible to simplify things...
"""


from pythiaplotter.utils.pdgid_converter import pdgid_to_string
import json
import pythiaplotter.utils.logging_config
import logging
from pkg_resources import resource_string


log = logging.getLogger(__name__)


# Hold user-defined settings from JSON file
# TODO: allow for user-defined JSON files
config_file = "printers/dot_config.json"
try:
    settings = json.loads(resource_string('pythiaplotter', config_file))
except IOError as e:
    log.exception("Cannot load settings file %s - no such file\n" % config_file)
    raise
except ValueError as e:
    log.exception("Problem parsing settings file %s\n" % config_file)
    raise

interesting_pdgids = settings.keys()[:]
non_pdgid_keys = ["_comment", "graph", "default", "initial", "final"]
interesting_pdgids = [i for i in interesting_pdgids if i not in non_pdgid_keys]


def load_json_settings(json_dict, attr):
    """Load dict from json_dict into attr dict. Checks to see if null value."""
    if json_dict:
        for key, value in json_dict.iteritems():
            attr[key] = value


def get_particle_label(particle, fancy):
    """Return string for particle label to be displayed on graph

    fancy: if True, will use HTML/unicode in labels
    """
    if fancy:
        label = r"<{0}: {1},  p<SUB>T</SUB>: {2:.2f}<br/>&eta;: {3:.2f},  &phi;: {4:.2f}>".format(
                particle.barcode, pdgid_to_string(particle.pdgid),
                particle.pt, particle.eta, particle.phi)
        label = label.replace("inf", "&#x221e;")
        return label
    else:
        return '"{0}: {1}, pT: {2:.2f}, eta: {3:.2f}, phi: {4:.2f}"'.format(
            particle.barcode, pdgid_to_string(particle.pdgid),
            particle.pt, particle.eta, particle.phi)


class DotEdgeAttr(object):
    """Hold display attributes for edge in dot graph

    edge: dict. Holds properties for this edge.
    fancy: if True, will use HTML/unicode in labels

    Auto-generates attributes from JSON file.
    """

    def __init__(self, edge, fancy=False):
        """

        :param edge: dict of edge properties
        :param fancy: bool. If True, uses HTML & unicode
        :return:
        """
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in edge.keys():  # edge represents a particle
            self.add_particle_attr(edge, fancy)
        else:
            self.add_line_attr(edge)

    def __repr__(self):
        return "DotEdgeAttrRepr"

    def __str__(self):
        """Print edge attributes in dot-friendly format"""
        attr_list = ['{0}={1}'.format(*it) for it in self.attr.iteritems()]
        return "[{0}]".format(", ".join(attr_list)) if attr_list else ""

    def add_line_attr(self, edge):
        """Simple line to represent relationship between particles"""
        pass

    def add_particle_attr(self, edge, fancy):
        """Style line as particle.
        Uses external config file to get PDGID-specific settings, as well as
        initial & final state particles.

        fancy: if True, will use HTML/unicode in labels
        """
        particle = edge["particle"]

        # Displayed edge label
        self.attr["label"] = get_particle_label(particle, fancy)

        # load default edge styling
        load_json_settings(settings["default"]["edge"], self.attr)

        # style initial & final state
        if particle.initial_state:
            load_json_settings(settings["initial"]["edge"], self.attr)
        elif particle.final_state:
            load_json_settings(settings["final"]["edge"], self.attr)

        # other interesting particles
        pid = str(abs(particle.pdgid))
        if pid in interesting_pdgids:
            load_json_settings(settings[pid]["edge"], self.attr)


class DotNodeAttr(object):
    """Hold display attributes for node in dot graph

    Auto-generates attributes from JSON file.
    """

    def __init__(self, node, fancy=False):
        """
        :param node: dict of node properties.
        :param fancy: bool. If True, uses HTML & unicode
        :return:
        """
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in node.keys():  # node represents a particle
            self.add_particle_attr(node, fancy)
        else:
            self.add_point_attr(node)

    def __repr__(self):
        return "DotNodeAttrRepr"

    def __str__(self):
        """Print node attributes in dot-friendly format"""
        attr_list = ['{0}={1}'.format(*it) for it in self.attr.iteritems()]
        return "[{0}]".format(", ".join(attr_list))

    def add_point_attr(self, node, show_barcode=False):
        """Simple point to show intersection of particles in EDGE representation

        show_barcode: shows the node/vertex barcode, for debugging purposes.
        """
        self.attr["shape"] = "circle" if show_barcode else "point"

    def add_particle_attr(self, node, fancy):
        """Style node as particle

        fancy: if True, will use HTML/unicode in labels

        Uses external config file to get PDGID-specific settings, as well as
        initial & final state particles.
        """
        particle = node["particle"]

        # Displayed node label
        self.attr["label"] = get_particle_label(particle, fancy)

        # default node styling
        load_json_settings(settings["default"]["node"], self.attr)

        # style initial & final state
        if particle.initial_state:
            load_json_settings(settings["initial"]["node"], self.attr)
        elif particle.final_state:
            load_json_settings(settings["final"]["node"], self.attr)

        # other interesting particles
        # do last so it overrides other initial/final settings
        pid = str(abs(particle.pdgid))
        if pid in interesting_pdgids:
            load_json_settings(settings[pid]["node"], self.attr)


class DotGraphAttr(object):
    """Hold Graphviz attributes for the graph as whole.

    Auto-generates attributes from JSON file.
    """

    def __init__(self, graph):
        self.graph = graph
        self.attr = {}
        load_json_settings(settings["graph"], self.attr)

    def __repr__(self):
        attr_list = ['{0}="{1}"'.format(*it) for it in self.attr.iteritems()]
        return "DotGraphAttr(attr=dict({0}))".format(", ".join(attr_list))

    def __str__(self):
        """Print graph attributes in dot-friendly format"""
        attr_list = ['{0}="{1}";'.format(*it) for it in self.attr.iteritems()]
        return "\t{0}".format("\n\t".join(attr_list))
