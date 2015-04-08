"""
Print Graph using dot/graphviz

Aim to be fairly generic - so can have particles as edges or nodes. All we
do is attach display attributes to each node/edge, then print these to file.

Several stages:
1. Go through nodes & edges and attach display attributes
2. Write to dot format
3. Render to PDF
"""


import utils.logging_config
import logging
import os.path
from subprocess import call
from display_classes import DotNodeAttr, DotEdgeAttr


log = logging.getLogger(__name__)


class DotPrinter(object):
    """Class to easily print event to file using dot/Graphviz"""

    def __init__(self, gv_filename, pdf_filename):
        self.gv_filename = gv_filename
        self.pdf_filename = pdf_filename

    def print_event(self, event):
        """Inclusive function to do the various stages easily"""
        self.event = event
        self.add_display_attr(event.graph)
        self.write_dot(event, self.gv_filename)
        self.print_pdf(self.gv_filename, self.pdf_filename)

    def add_display_attr(self, graph):
        """Add display attribute to nodes & edges"""
        for node_ind in graph.nodes():
            node = graph.node[node_ind]
            node["attr"] = DotNodeAttr(node)

        for edges_ind in graph.edges():
            edge = graph.edge[edges_ind[0]][edges_ind[1]]
            edge["attr"] = DotEdgeAttr(edge)

    def write_dot(self, event, dot_filename):
        """Write event graph to file in dot format"""

        log.info("Writing GraphViz file to %s" % dot_filename)
        with open(dot_filename, "w") as dot_file:

            # Header-type info
            dot_file.write("digraph g {\n"
                          "\trankdir=LR;\n"
                          "\tranksep=0.4;\n"
                          "\tnodesep=0.4;\n")

            # Add event info to plot
            if event.label:
                lbl = "<FONT POINT-SIZE=\"40\">{0}<BR/>".format(event.label)
                if event.run_num:
                    lbl += "Run: {0} <BR/>".foramt(event.run_num)
                if event.lumi_section:
                    lbl += "LS: {0} <BR/>".format(event.lumi_section)
                if event.run_num:
                    lbl += "Event: {0}<BR/>".format(event.event_num)
                # lbl += "Key:<BR/>"
                # lbl += "green"
                lbl += "</FONT>"
                dot_file.write("\tlabel=<{0}>;\n".format(lbl))
                dot_file.write("\tlabelloc=top;\n")
                dot_file.write("\tlabeljust=left;\n") # this doesn't work

            graph = event.graph
            # Now write all the nodes to file,
            # with their display attributes
            for node in graph.nodes():
                # Maybe use this form for smaller files when in NODE repr?
                # children = ' '.join(graph.successors())
                # dot_file.write("{0} -> {{ {1} }}").format(node, children)
                dot_file.write("\t{0} {1}\n".format(node, graph.node[node]["attr"]))

            # Same with edges
            for edge_ind in graph.edges():
                edge = graph[edge_ind[0]][edge_ind[1]]
                dot_file.write("\t{0} -> {1} {2}\n".format(edge_ind[0], edge_ind[1], edge["attr"]))

            # Set all initial particles to be level in diagram
            initial = ' '.join([str(node) for node in graph.nodes() if graph.node[node]['particle'].initial_state])
            dot_file.write("\t{{rank=same; {0} }} "
                          "// initial particles on same level\n".format(initial))

            dot_file.write("}\n")

    def print_pdf(self, dot_filename, pdf_filename):
        """Run GraphViz file through dot to produce a PDF."""

        log.info("Writing PDF to %s", pdf_filename)

        # Do 2 stages: make a PostScript file, then convert to PDF.
        # This makes the PDF searchable.
        # ps_filename = pdf_filename.replace(".pdf", ".ps")
        # psargs = ["dot", "-Tps2", dot_filename, "-o", ps_filename]
        # call(psargs)
        # pdfargs = ["ps2pdf", ps_filename, pdf_filename]
        # call(psargs)

        # Or do straight to PDF:
        dotargs = ["dot", "-Tpdf", dot_filename, "-o", pdf_filename]
        call(dotargs)

        # print ""
        # print "To re-run:"
        # print ' '.join(psargs)
        # print ' '.join(pdfargs)
        # print ""
