"""
Print Graph using dot/graphviz

Aim to be fairly generic - so can have particles as edges or nodes. All we
do is attach display attributes to each node/edge, then print these to file.

Several stages:
1. Go through nodes & edges and attach display attributes
2. Write to dot format
3. Render to PDF
"""


import os.path
from subprocess import call
from display_classes import DotNodeAttr, DotEdgeAttr


def add_display_attr(graph, opts):
    """Add display attribute to nodes & edges"""
    for node_ind in graph.nodes():
        node = graph[node]
        node["attr"] = DotNodeAttr(node)

    for edges_ind in graph.edges():
        edge = graph.edge[edges_ind[0]][edges_ind[1]]
        edge["attr"] = DotEdgeAttr(edge)


def write_dot(event, dot_filename):
    """Write event graph to file in dot format"""

    print "Writing GraphViz file to %s" % dot_filename
    with open(dot_filename, "w") as dot_file:

        # Header-type info
        gv_file.write("digraph g {\n"
                      "\trankdir=LR;\n"
                      "\tranksep=0.4\n"
                      "\tnodesep=0.4\n")

        # TODO: print event info

        graph = event.graph
        # Now write all the nodes and edges to file,
        # with their display attributes
        for node in graph.nodes():
            # Maybe use this form for smaller files when in NODE repr?
            # children = ' '.join(graph.successors())
            # gv_file.write("{0} -> {{ {1} }}").format(node, children)
            gv_file.write("{0} {1}\n".format(node, graph[node]["attr"]))

        # Same with edges
        for edge_ind in graph.edges():
            edge = graph[edge_ind[0]][edge_ind[1]]
            gv_file.write("{0} -> {1} {2}\n".format(edge_ind[0], edge_ind[1], edge["attr"]))

        # Set all initial particles to be level in diagram
        initial = ' '.join([str(node) for node in graph.nodes() if graph[node]['particle'].initial_state])
        gv_file.write("\t{{rank=same; {0} }} "
                      "// initial particles on same level\n".format(initial))

        gv_file.write("}\n")


def print_pdf(dot_filename, pdf_filename):
    """Run GraphViz file through dot to produce a PDF."""
    # Do 2 stages: make a PostScript file, then convert to PDF.
    # This makes the PDF searchable.
    ps_filename = pdf_filename.replace(".pdf", ".ps")
    psargs = ["dot", "-Tps2", dot_filename, "-o", ps_filename]
    call(psargs)
    psargs = ["ps2pdf", ps_filename, pdf_filename]
    call(psargs)

    # Or do straight to PDF:
    # pdfargs = ["dot", "-Tpdf", dot_filename, "-o", pdf_filename]
    # call(pdfargs)

    print ""
    print "To re-run:"
    print ' '.join(dotargs)
    print ' '.join(psargs)
    print ""
