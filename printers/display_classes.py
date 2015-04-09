"""
Classes to describe visual representation
"""


from utils.pdgid_converter import pdgid_to_string
import json


# Hold user-defined settings from JSON file
config_file = "printers/dot_config.json"
with open(config_file) as jfile:
    data = json.load(jfile)

interesting_pdgids = data.keys()[:]
non_pdgids = ["_comment", "default", "initial", "final"]
interesting_pdgids = [int(i) for i in interesting_pdgids if i not in non_pdgids]


class DotEdgeAttr(object):
    """Hold display attributes for edge in dot graph"""

    def __init__(self, edge):
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in edge.keys():  # edge represents a particle
            self.add_particle_attr(edge)
        else:
            self.add_line_attr(edge)

    def __repr__(self):
        return "DotEdgeAttrRepr"

    def __str__(self):
        attr_list = ['{0}="{1}"'.format(i[0], i[1]) for i in self.attr.iteritems()]
        return "[{0}]".format(", ".join(attr_list)) if attr_list else ""

    def add_line_attr(self, edge):
        """Simple line to represent relationship between particles"""
        pass

    def add_particle_attr(self, edge):
        """Style line as particle.
        Uses external config file to get PDGID-specific settings, as well as
        initial & final state particles.
        """
        pass


class DotNodeAttr(object):
    """Hold display attributes for node in dot graph"""

    def __init__(self, node):
        self.attr = {}  # dict to hold attributes - key must be same as in GV
        if "particle" in node.keys():  # node represents a particle
            self.add_particle_attr(node)
        else:
            self.add_point_attr(node)

    def __repr__(self):
        return "DotNodeAttrRepr"

    def __str__(self):
        attr_list = ['{0}="{1}"'.format(i[0], i[1]) for i in self.attr.iteritems()]
        return "[{0}]".format(", ".join(attr_list))

    def add_point_attr(self, node):
        """Simple point to represent intersection of particles"""
        self.attr["shape"] = "point"

    def add_particle_attr(self, node):
        """Style node as particle
        Uses external config file to get PDGID-specific settings, as well as
        initial & final state particles.
        """
        particle = node["particle"]

        # Displayed node label
        self.attr["label"] = "{0}: {1}".format(particle.barcode,
                                               pdgid_to_string(particle.pdgid))

        # default stylings, if they exist
        if data["default"]["node"]:
            for key, value in data["default"]["node"].iteritems():
                self.attr[key] = value

        # style initial & final state
        if particle.initial_state:
            for key, value in data["initial"].iteritems():
                self.attr[key] = value
        elif particle.final_state:
            for key, value in data["final"].iteritems():
                self.attr[key] = value

        # other interesting particles
        if abs(particle.pdgid) in interesting_pdgids:
            for key, value in data[str(abs(particle.pdgid))].iteritems():
                self.attr[key] = value