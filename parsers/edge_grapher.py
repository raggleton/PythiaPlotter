"""
Attaches particles etc to a NetworkX graph, when EDGES represent particles.

Note about convention:

A particle's "out" node is the one from which it is outgoing. Similarly, its
"in" node is the one into which it is incoming.
e.g. a -->-- b : a is the "out" node, b is the "in" node for this edge.

An "incoming edge" to a node is an edge whose destination node is the node
in question. Similarly, an "outgoing edge" from a node is any edge whose source
is the node in question.
e.g. c ---p->-- d: here p is an incoming edge to node d, whilst it is also an
outgoing edge for node c.
"""


import utils.logging_config
import logging
import networkx as nx


log = logging.getLogger(__name__)


def assign_particles_edges(particles, remove_redundants=True):
    """
    Attach particles to NetworkX directed graph when EDGES represent particles.

    Particles must have vtx_in_barcode and vtx_out_barcode attributes.
    """

    gr = nx.DiGraph(attr=None)

    initial_nodes = []  # to store outgoing nodes for initial state particles

    # assign an edge for each Particle object, preserving direction
    for particle in particles:
        log.debug(particle.__dict__)
        gr.add_edge(particle.vtx_out_barcode, particle.vtx_in_barcode,
                    barcode=particle.barcode, particle=particle)
        if particle.initial_state:
            initial_nodes.append(particle.vtx_out_barcode)

    # get set of unique vertices, assign to graph as nodes
    out_barcodes = [p.vtx_out_barcode for p in particles]
    in_barcodes = [p.vtx_in_barcode for p in particles]
    nodes = set(out_barcodes + in_barcodes)
    for n in nodes:
        # mark node as initial state or not, so we can align them on graph
        initial_state = True if n in initial_nodes else False
        gr.add_node(n, initial_state=initial_state)

    log.debug(gr.edges())
    log.debug(gr.nodes())

    # optionally remove redundant edges
    if remove_redundants:
        remove_redundant_edges(gr)

        log.debug(gr.nodes())
        log.debug(gr.edges())

    return gr


def remove_redundant_edges(graph):
    """
    Remove redundant particle edges - i.e. when you have a particles which has
    1 particle incoming to its outgoing node and has the same PDGID,
    and >0 outgoing particles

    e.g.
    --q-->-g->-g->-g->--u---->
        |             |
    --q->             --ubar->

    Remove the middle gluon and last gluons, since they add no information.

    These are useful to keep if considering MC internal workings,
    but otherwise are just confusing and a waste of space.
    """
    # TODO: fix me :( write some tests!

    remove_nodes = set()  # use a set here to only keep unique nodes
    for edge_ind in graph.edges():  # (b,c)
        edge = graph[edge_ind[0]][edge_ind[1]]  # {barcode:...}

        # get all incoming edges to this particle's out node,
        # and all outgoing edges from this particle's in node
        in_edges_id = graph.in_edges(edge_ind[0])  # [(a,b), ...]
        out_edges_id = graph.out_edges(edge_ind[1])
        if len(in_edges_id) == 1 and len(out_edges_id) != 0:

            # dict of objets for this edge
            in_edge = graph[in_edges_id[0][0]][in_edges_id[0][1]]

            if in_edge["particle"].pdgid == edge["particle"].pdgid:

                log.debug("removing redundant edges")
                log.debug(edge)
                particle = edge["particle"]

                out_node = edge_ind[0]  # b
                in_node = edge_ind[1]  # c

                # set incoming edge's node to this edge's incoming node
                # and mark this edge's outgoing node for removal
                graph.add_edge(in_edges_id[0][0], in_node,
                               barcode=particle.barcode, particle=particle)
                remove_nodes.add(out_node)

    # Remove all redundant nodes, also removes the associated edges usefully
    for node in remove_nodes:
        graph.remove_node(node)