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
from string import Template
from subprocess import call, PIPE, Popen
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str
from .dot_display_classes import DotNodeAttr, DotEdgeAttr, DotGraphAttr


log = get_logger(__name__)


class DotPrinter(object):
    """Class to print event to file using Graphviz"""

    def __init__(self, opts):
        """

        Parameters
        ----------
        opts : Argparse.Namespace
            Set of options from the arg parser.

        Attributes
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
        self.output_filename = opts.output
        self.renderer = opts.layout
        self.output_format = opts.outputFormat
        self.make_diagram = not opts.noOutput
        self.write_gv = opts.saveGraphviz
        if self.write_gv:
            self.gv_filename = os.path.splitext(self.output_filename)[0] + ".gv"
        else:
            self.gv_filename = None

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
        add_display_attr(event, fancy)
        gv_str = construct_gv_full(event)
        if self.make_diagram:
            run_cmds = print_diagram(gv_str=gv_str,
                                     output_filename=self.output_filename,
                                     renderer=self.renderer,
                                     output_format=self.output_format)
        if self.write_gv:
            write_gv(gv_str, self.gv_filename)


def add_display_attr(event, fancy):
    """Auto add display attribute to graph, nodes & edges

    Parameters
    ----------
    event : Event
        Event to process
    fancy : bool
        If True, will use HTML/unicode in labels
    """
    graph = event.graph
    graph.graph["attr"] = DotGraphAttr(graph)

    for _, node_data in graph.nodes_iter(data=True):
        node_data["attr"] = DotNodeAttr(node_data, fancy)

    for _, _, edge_data in graph.edges_iter(data=True):
        edge_data["attr"] = DotEdgeAttr(edge_data, fancy)


def construct_gv_full(event):
    """Turn event graph into Graphviz string in DOT language

    Parameters
    ----------
    event : Event

    Returns
    -------
    str
    """
    graph = event.graph

    # Header-type info with graph-wide settings
    gv_str = ["digraph g {"]
    gv_str.append("{attr}".format(**graph.graph))

    # Write all the nodes to file, with their display attributes
    for node, node_data in graph.nodes_iter(data=True):
        gv_str.append("{0} {attr};".format(node, **node_data))

    # Write all the edges to file, with their display attributes
    for out_node, in_node, edge_data in graph.edges_iter(data=True):
        gv_str.append("{0} -> {1} {attr};".format(out_node, in_node, **edge_data))

    # Set all initial particles to be level in diagram
    initial = ' '.join([str(node) for node, node_data
                        in graph.nodes_iter(data=True)
                        if len(graph.predecessors(node)) == 0])
    gv_str.append("{{rank=same; {0} }}; "
                    "// initial particles on same level".format(initial))
    gv_str.append("}")
    gv_str = "\n".join(gv_str)

    # Fill in template with any data
    gv_str = Template(gv_str).safe_substitute(event.__dict__)

    return gv_str


def write_gv(gv_str, gv_filename):
    """Write event graph to file in Graphviz format"""

    log.info("Writing Graphviz file to %s", gv_filename)
    with open(gv_filename, "w") as gv_file:
        gv_file.write(gv_str)


def print_diagram(gv_str, output_filename, renderer, output_format):
    """Pass graph in DOT language to a Graphviz program to produce a diagram.

    Parameters
    ----------
    gv_str : str
        Graph contents in DOT language

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
    if output_format is None:
        raise RuntimeError("Need an output format for graphviz")

    log.info("Printing diagram to %s", output_filename)
    run_cmds = []

    if output_format == "ps" or output_format == "ps2":
        # Do 2 stages: make a PostScript file, then convert to PDF.
        ps_filename = os.path.splitext(output_filename)[0] + ".ps"

        if output_format == "ps":  # hmm or should we get user to do this
            output_format += ":cairo"

        dot_args = [renderer, "-T" + output_format, "-o", ps_filename]
        p = Popen(dot_args, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input=gv_str.encode())
        if p.returncode != 0:
            raise RuntimeError(err)

        if output_filename.endswith(".pdf"):
            pdfargs = ["ps2pdf", ps_filename, output_filename]
            call(pdfargs)

            rmargs = ["rm", ps_filename]
            call(rmargs)

    elif output_format is not None:
        dot_args = [renderer, "-T" + output_format, "-o", output_filename]
        p = Popen(dot_args, stdin=PIPE, stderr=PIPE)
        out, err = p.communicate(input=gv_str.encode())
        if p.returncode != 0:
            raise RuntimeError(err)

    return run_cmds
