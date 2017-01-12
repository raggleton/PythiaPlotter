"""
Print graph using Graphviz

Aim to be fairly generic, so can have particles as edges or nodes. All we
do is attach display attributes to each node/edge, then print these to file.

Several stages:
1. Go through nodes & edges and attach display attributes [add_display_attr()]
2. Write to Graphviz format file [write_gv()]
3. Render to PDF [print_pdf()]
"""


import PythiaPlotter.utils.logging_config
import logging
from subprocess import call
from dot_display_classes import DotNodeAttr, DotEdgeAttr, DotGraphAttr


log = logging.getLogger(__name__)


class DotPrinter(object):
    """Class to print event to file using Graphviz"""

    def __init__(self, gv_filename, pdf_filename, renderer="dot", output_format="pdf"):
        self.gv_filename = gv_filename
        self.pdf_filename = pdf_filename
        self.renderer = renderer
        self.output_format = output_format

    def __repr__(self):
        return "{0}(gv_filename={1[gv_filename]}, pdf_filename={1[pdf_filename]}, " \
               "renderer={1[pdf]}, output_format={1[output_format]})".format(self.__class__.__name__, self)

    def print_event(self, event, pdf=True):
        """Inclusive function to do the various stages of printing easily

        pdf: bool. If True, the chosen renderer converts the Graphviz
            file to a graph PDF
        """
        event = event
        fancy = self.output_format in ["ps", "pdf"]
        add_display_attr(event.graph, fancy)
        write_gv(event, self.gv_filename)
        if pdf:
            print_pdf(gv_filename=self.gv_filename, pdf_filename=self.pdf_filename,
                      renderer=self.renderer, output_format=self.output_format)


def add_display_attr(graph, fancy):
    """Auto add display attribute to graph, nodes & edges

    fancy: if True, will use HTML/unicode in labels
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

    log.info("Writing Graphviz file to %s" % gv_filename)
    with open(gv_filename, "w") as gv_file:

        graph = event.graph

        # Header-type info with graph-wide settings
        gv_file.write("digraph g {\n")
        gv_file.write("{attr}\n".format(**graph.graph))

        # Add event info to plot
        lbl = ""
        if event.label:
            # Event title
            lbl = '<FONT POINT-SIZE="45"><B>{0}' \
                  '</B></FONT><BR/>'.format(event.label)
        lbl += '<FONT POINT-SIZE="40">  <BR/>'
        # Event info
        # Keep event.label as a title, not in attribute list
        evt_lbl = [x for x in event.__str__().split("\n")
                   if not (x.startswith("label") or x.startswith("Event"))]
        lbl += '<BR/>'.join(evt_lbl)
        lbl += '</FONT>'
        gv_file.write("\tlabel=<{0}>;\n".format(lbl))

        # Now print the graph to file

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


def print_pdf(gv_filename, pdf_filename, renderer, output_format):
    """Run Graphviz file through a Graphviz program to produce a PDF.

    renderer: Graphviz program to use.

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
