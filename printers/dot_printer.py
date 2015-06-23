"""
Print graph using GraphViz

Aim to be fairly generic, so can have particles as edges or nodes. All we
do is attach display attributes to each node/edge, then print these to file.

Several stages:
1. Go through nodes & edges and attach display attributes [add_display_attr()]
2. Write to GraphViz format file [write_gv()]
3. Render to PDF [print_pdf()]
"""


import utils.logging_config
import logging
import os.path
from subprocess import call
from display_classes import DotNodeAttr, DotEdgeAttr, DotGraphAttr


log = logging.getLogger(__name__)


class DotPrinter(object):
    """Class to print event to file using Graphviz"""

    def __init__(self, gv_filename, pdf_filename, renderer="dot", output_format="pdf"):
        self.gv_filename = gv_filename
        self.pdf_filename = pdf_filename
        self.renderer = renderer
        self.output_format = output_format

    def __repr__(self):
        return "{0}(gv_filename={1[barcode}, pdf_filename={1[pdf_filename]}, " \
               "renderer={1[pdf]}, output_format={1[output_format]})".format(
               self.__class__.__name__, self)

    def print_event(self, event):
        """Inclusive function to do the various stages of printing easily"""
        self.event = event
        self.add_display_attr(event.graph)
        self.write_gv(event, self.gv_filename)
        self.print_pdf(gv_filename=self.gv_filename,
                       pdf_filename=self.pdf_filename,
                       renderer=self.renderer,
                       output_format=self.output_format)

    @staticmethod
    def add_display_attr(graph):
        """Auto add display attribute to graph, nodes & edges"""

        graph.graph["attr"] = DotGraphAttr(graph)

        for node_ind in graph.nodes():
            graph.node[node_ind]["attr"] = DotNodeAttr(graph.node[node_ind])

        for edges_ind in graph.edges():
            # NB if graph is a MultiDiGraph then need to add extra index [0]
            # since could have multiple edge between same vertices
            edge = graph.edge[edges_ind[0]][edges_ind[1]]
            edge["attr"] = DotEdgeAttr(edge)

    @staticmethod
    def write_gv(event, gv_filename):
        """Write event graph to file in GraphViz format"""
        log.info("Writing GraphViz file to %s" % gv_filename)
        with open(gv_filename, "w") as dot_file:

            graph = event.graph

            # Header-type info with graph-wide settings
            dot_file.write("digraph g {\n")
            dot_file.write("{attr}\n".format(**graph.graph))

            # Add event info to plot
            lbl = ""
            if event.label:
                # Event title
                lbl = "<FONT POINT-SIZE=\"45\"><B>{0}</B></FONT><BR/>".format(event.label)
            lbl += "<FONT POINT-SIZE=\"40\">  <BR/>"
            # Event info
            # Keep event.label as a title, not in attribute list
            evt_lbl = [x for x in event.__str__().split("\n")
                       if not (x.startswith("label") or x.startswith("Event"))]
            lbl += '<BR/>'.join(evt_lbl)
            lbl += "</FONT>"
            dot_file.write("\tlabel=<{0}>;\n".format(lbl))

            # Now print the graph to file

            # Write all the nodes to file, with their display attributes
            for node in graph.nodes():
                # Maybe use this form for smaller files when in NODE repr?
                # Otherwise have line for *each* edge, even when parent same
                # children = ' '.join(graph.successors())
                # dot_file.write("{0} -> {{ {1} }}").format(node, children)
                dot_file.write("\t{0} {attr};\n".format(node, **graph.node[node]))

            # Write all the edges to file, with their display attributes
            for edge_ind in graph.edges():
                edge = graph[edge_ind[0]][edge_ind[1]]
                dot_file.write("\t{0} -> {1} {attr};\n".format(*edge_ind, **edge))

            # Set all initial particles to be level in diagram
            initial = ' '.join([str(node) for node in graph.nodes() if graph.node[node]['final_state']])
            dot_file.write("\t{{rank=same; {0} }}; "
                           "// initial particles on same level\n".format(initial))

            dot_file.write("}\n")

    @staticmethod
    def print_pdf(gv_filename, pdf_filename, renderer, output_format):
        """Run GraphViz file through a GraphViz program to produce a PDF.

        renderer: GraphViz program to use.

        output_format: ps, ps2, or pdf. Each has its own advantages.
            ps - uses ps:cairo. Obeys HTML tags & unicode, but not searchable
            ps2 - PDF searchable, but won't obey all HTML tags or unicode.
            pdf - obeys HTML but not searchable
        """

        log.info("Writing PDF to %s", pdf_filename)
        log.info("To re-run:")

        if output_format == "ps" or output_format == "ps2":
            # Do 2 stages: make a PostScript file, then convert to PDF.
            ps_filename = pdf_filename.replace(".pdf", ".ps")
            if output_format == "ps2":
                output_format += ":cairo"
            psargs = [renderer, "-T%s" % output_format, gv_filename, "-o", ps_filename]
            call(psargs)
            pdfargs = ["ps2pdf", ps_filename, pdf_filename]
            call(pdfargs)
            rmargs = ["rm", ps_filename]
            call(rmargs)
            log.info(" ".join(psargs))
            log.info(" ".join(pdfargs))
            log.info(" ".join(rmargs))
        elif output_format == "pdf":
            # Or do straight to PDF: fast, obeys HTML tags, but not searchable.
            dotargs = [renderer, "-Tpdf", gv_filename, "-o", pdf_filename]
            call(dotargs)
            log.info(" ".join(dotargs))
        else:
            raise Exception("'%s' is not a valid output_format option: use ps, ps2, or pdf" % output_format)
