"""Print graph using Graphviz.

Aim to be fairly generic, so can have particles as edges or nodes. All we
do is attach display attributes to each node/edge, then print these to file.

Several stages:
1. Go through nodes & edges and attach display attributes [add_display_attr()]
2. Write to Graphviz format file [write_gv()]
3. Render to file [print_diagram()]
"""


from __future__ import absolute_import
import os
from subprocess import call
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str
from .dot_display_classes import DotNodeAttr, DotEdgeAttr, DotGraphAttr


log = get_logger(__name__)


class DotPrinter(object):
    """Class to print event to file using Graphviz"""

    def __init__(self, output_filename, renderer="dot", output_format="pdf", make_diagram=True):
        """

        Parameters
        ----------
        output_filename : str
            Final output filename (e.g of the pdf, not the intermediate graphviz file)
        renderer : str, optional
            Graphviz program to use for rendering layout, default is dot since dealing with DAGs
        output_format : str, optional
            Output format for diagram. Defaults to PDF.
        make_diagram : bool, optional
            If True, the chosen renderer converts the Graphviz file to a graph diagram.

        Attributes
        ----------
        gv_filename : str
            Filename for intermediate Graphviz file
        """
        self.output_filename = output_filename
        self.gv_filename = os.path.splitext(self.output_filename)[0] + ".gv"
        self.renderer = renderer
        self.output_format = output_format or os.path.splitext(self.output_filename)[1][1:]
        self.make_diagram = make_diagram

    def __repr__(self):
        return generate_repr_str(self)

    def print_event(self, event):
        """Write the event diagram to Graphivz file and run the renderer.

        Parameters
        ----------
        event : Event
            Event to print
        """
        fancy = self.output_format in ["ps", "pdf"]
        add_display_attr(event.graph, fancy)
        write_gv(event, self.gv_filename)
        if self.make_diagram:
            print_diagram(gv_filename=self.gv_filename, output_filename=self.output_filename,
                          renderer=self.renderer, output_format=self.output_format)


def add_display_attr(graph, fancy):
    """Auto add display attribute to graph, nodes & edges

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to process
    fancy : bool
        If True, will use HTML/unicode in labels
    """

    graph.graph["attr"] = DotGraphAttr(graph)

    for _, node_data in graph.nodes_iter(data=True):
        node_data["attr"] = DotNodeAttr(node_data, fancy)

    for _, _, edge_data in graph.edges_iter(data=True):
        edge_data["attr"] = DotEdgeAttr(edge_data, fancy)


def write_nodes(graph, gv_file):
    """Write all node to file, with their display attributes"""
    for node, node_data in graph.nodes_iter(data=True):
        gv_file.write("\t{0} {attr};\n".format(node, **node_data))


def write_edges(graph, gv_file):
    """Write all edges to file, with their display attributes"""
    for out_node, in_node, edge_data in graph.edges_iter(data=True):
        gv_file.write("\t{0} -> {1} {attr};\n".format(out_node, in_node, **edge_data))


def write_gv(event, gv_filename):
    """Write event graph to file in Graphviz format"""

    log.info("Writing Graphviz file to %s", gv_filename)
    with open(gv_filename, "w") as gv_file:

        graph = event.graph

        # Header-type info with graph-wide settings
        gv_file.write("digraph g {\n")
        gv_file.write("{attr}\n".format(**graph.graph))

        # Write all the nodes to file, with their display attributes
        write_nodes(graph, gv_file)

        # Write all the edges to file, with their display attributes
        write_edges(graph, gv_file)

        # Set all initial particles to be level in diagram
        initial = ' '.join([str(node) for node, node_data in graph.nodes_iter(data=True)
                            if node_data['initial_state']])
        gv_file.write("\t{{rank=same; {0} }}; "
                      "// initial particles on same level\n".format(initial))

        gv_file.write("}\n")


def print_diagram(gv_filename, output_filename, renderer, output_format):
    """Run Graphviz file through a Graphviz program to produce a final diagram.

    Parameters
    ----------
    gv_filename : str
        Name of graphviz file to process

    output_filename : str
        Final diagram filename

    renderer : str
        Graphviz program to use

    output_format : str
        Each has its own advantages, see http://www.graphviz.org/doc/info/output.html

        * ps - uses ps:cairo. Obeys HTML tags & unicode, but not searchable
        * ps2 - PDF searchable, but won't obey all HTML tags or unicode.
        * pdf - obeys HTML but not searchable
    """

    log.info("Printing diagram to %s", output_filename)
    log.info("To re-run:")

    if output_format == "ps" or output_format == "ps2":
        # Do 2 stages: make a PostScript file, then convert to PDF.
        ps_filename = os.path.splitext(output_filename)[0] + ".ps"

        if output_format == "ps":  # hmm or should we get user to do this
            output_format += ":cairo"

        psargs = [renderer, "-T" + output_format, gv_filename, "-o", ps_filename]
        log.info(" ".join(psargs))
        call(psargs)

        if output_filename.endswith(".pdf"):
            pdfargs = ["ps2pdf", ps_filename, output_filename]
            log.info(" ".join(pdfargs))
            call(pdfargs)

            rmargs = ["rm", ps_filename]
            log.info(" ".join(rmargs))
            call(rmargs)

    elif output_format is not None:
        dotargs = [renderer, "-T" + output_format, gv_filename, "-o", output_filename]
        log.info(" ".join(dotargs))
        call(dotargs)
    else:
        raise RuntimeError("Need an output format for graphviz")
