"""
Classes to describe visual representation
"""


from utils.pdgid_converter import pdgid_to_string


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
        return "[{0}]".format(", ".join(attr_list))

    def add_line_attr(self, edge):
        """Simple line to represent relationship between particles"""
        pass

    def add_particle_attr(self, edge):
        """Style line as particle according to PDGID, initial/final state, special, etc"""
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
        """Style node as particle according to PDGID, initial/final state, special, etc"""
        particle = node["particle"]
        self.attr["label"] = " {0}: {1}".format(particle.barcode,
                                                pdgid_to_string(particle.pdgid))

        if particle.initial_state:
            self.attr["style"] = "filled"
            self.attr["shape"] = "circle"
        elif particle.final_state:
            self.attr["style"] = "filled"
            self.attr["shape"] = "box"

        # if particle.isInteresting:
        #     self.attr["style"] = "filled"