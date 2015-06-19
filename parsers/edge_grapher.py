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


def assign_particles_edges(edge_particles, remove_redundants=True):
    """
    Attach particles to directed graph edges when EDGES represent particles.

    edge_particles must be a list of EdgeParticle objects.
    """

    gr = nx.DiGraph(attr=None)  # placeholder attr for later in printer

    # assign an edge for each Particle object, preserving direction
    # note that NetworkX auto adds nodes when edges are added
    for ep in edge_particles:
        log.debug("Adding edge %s -> %s" % (ep.vtx_out_barcode, ep.vtx_in_barcode))

        gr.add_edge(ep.vtx_out_barcode, ep.vtx_in_barcode,
                    barcode=ep.barcode, particle=ep.particle)

    # Get in-degree for nodes so we can mark the initial state ones
    # (those with no incoming edges) and their particles
    for n, i in gr.in_degree_iter(gr.nodes()):
        gr.node[n]['initial_state'] = False
        if i == 0:
            for e, f in gr.out_edges_iter(n):
                gr.edge[e][f]['particle'].initial_state = True

    # Do same for final-state nodes/particles (nodes which have no outgoing edges)
    for n, i in gr.out_degree_iter(gr.nodes()):
        gr.node[n]['final_state'] = False
        if i == 0:
            gr.node[n]['final_state'] = True
            for e, f in gr.in_edges_iter(n):
                gr.edge[e][f]['particle'].final_state = True

    log.debug("Edges after assigning: %s" % gr.edges())
    log.debug("Nodes after assigning: %s" % gr.nodes())

    # optionally remove redundant edges
    if remove_redundants:
        remove_redundant_edges(gr)

        log.debug("remove_redundant Edges:%s" % gr.edges())
        log.debug("remove_redundant Nodes: %s" % gr.nodes())

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