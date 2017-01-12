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


import logging
import PythiaPlotter.utils.logging_config
import networkx as nx


log = logging.getLogger(__name__)


def assign_particles_edges(edge_particles, remove_redundants=True):
    """Attach particles to directed graph edges when EDGES represent particles.

    The graph itself is a networkx MultiDiGraph: a directed graph, that can have
    multiple edges between 2 nodes. We distinguish these via the edge['barcode']
    attribute, where the barcode value = particle barcode. We can use
    MultiDiGraph.edges(data=True) to correctly iterate over *all* edges.


    Additionally marks particles as initial/final state as necessary, based on
    whether they have any parents/children, respectively.


    edge_particles: list of EdgeParticle objects
        The Particle in each EdgeParticle will be assigned to a graph edge,
        using the vertex information in the EdgeParticle object.

    remove_redundants: bool
        Optionally remove redundant particles from the graph.
        'Redundants' carry no extra physics information, but are only used
        internally by Pythia, etc

    Returns a networkx.MultiDiGraph object.
    """

    gr = nx.MultiDiGraph(attr=None)  # placeholder attr for later in printer

    # assign an edge for each Particle object, preserving direction
    # note that NetworkX auto adds nodes when edges are added
    for ep in edge_particles:
        log.debug("Add edge %s > %s for %s", ep.vtx_out_barcode, ep.vtx_in_barcode, ep.particle)

        gr.add_edge(ep.vtx_out_barcode, ep.vtx_in_barcode,
                    barcode=ep.barcode, particle=ep.particle)

    # Get in-degree for nodes so we can mark the initial state ones
    # (those with no incoming edges) and their particles
    for node, degree in gr.in_degree_iter(gr.nodes()):
        gr.node[node]['initial_state'] = False
        if degree == 0:
            gr.node[node]['initial_state'] = True
            for e, f, edge_data in gr.out_edges_iter(node, data=True):
                edge_data['particle'].initial_state = True

    # Do same for final-state nodes/particles (nodes which have no outgoing edges)
    for node, degree in gr.out_degree_iter(gr.nodes()):
        gr.node[node]['final_state'] = False
        if degree == 0:
            gr.node[node]['final_state'] = True
            for e, f, edge_data in gr.in_edges_iter(node, data=True):
                edge_data['particle'].final_state = True

    log.debug("Edges after assigning: %s", gr.edges())
    log.debug("Nodes after assigning: %s", gr.nodes())

    # optionally remove redundant edges
    if remove_redundants:
        remove_redundant_edges(gr)

        log.debug("After remove_redundant Edges:%s", gr.edges())
        log.debug("After remove_redundant Particles: %s", [gr[degree][j]['particle']
                                                           for degree, j in gr.edges()])
        log.debug("After remove_redundant Nodes: %s", gr.nodes())

    return gr


def remove_redundant_edges(graph):
    """Remove redundant particle edges from a graph.

    A particle is redundant when:
    1) > 0 'child' particles (those outgoing from the particle's incoming node
    - this ensures we don't remove final-state particles)
    2) 1 'parent' particle with same PDGID (incoming into the particle's
    outgoing node - also ensures we don't remove initial-state particles)
    3) 0 'sibling' particles (those outgoing from the particle's outgoing node)
    Note that NetworkX includes an edge as its own sibling, so actually we
    require len(sibling_edges) == 1

    e.g.

    --q-->-g->-g->-g->--u---->
        |             |
    --q->             --ubar->


    Remove the middle gluon and last gluon, since they add no information.

    These redundants are useful to keep if considering MC internal workings,
    but otherwise are just confusing and a waste of space.

    Since it loops over the list of graph edges, we can only remove one edge in
    a loop, otherwise adding extra/replacement edges ruins the sibling counting
    and doesn't remove redundants. So the method loops through the graph edges
    until there are no more redundant edges.

    Since we are dealing with MultiDiGraph, we have to be careful about siblings
    that actually span the same set of nodes - these shouldn't be removed.

    There is probably a more sensible way to do this, currently brute
    force and slow.
    """

    done_removing = False
    while not done_removing:

        done_removing = True
        remove_nodes = set()  # use a set here to only keep unique nodes

        for out_node, in_node, edge_data in graph.edges_iter(data=True):
            log.debug("Doing edge:", )
            log.debug([out_node, in_node])

            # get all incoming edges to this particle's out node (parents)
            parent_edges = graph.in_edges(out_node)  # [(a,b), ...]
            # get all outgoing edges from this particle's out node (siblings)
            sibling_edges = graph.out_edges(out_node)
            # get all outgoing edges from this particle's in node (children)
            child_edges = graph.out_edges(in_node)
            log.debug("Parent edges: %s", parent_edges)
            log.debug("Child edges: %s", child_edges)
            log.debug("Sibling edges: %s", sibling_edges)
            if len(parent_edges) == 1 and len(child_edges) != 0 and len(sibling_edges) == 1:

                # dict of objects for this edge
                in_edge = graph[parent_edges[0][0]][parent_edges[0][1]]

                # Do removal if parent PDGID matches
                if in_edge["particle"].pdgid == edge_data["particle"].pdgid:

                    done_removing = False

                    log.debug("Removing redundant edge %s", edge_data)
                    particle = edge_data["particle"]

                    # set incoming edges' incoming node to this edge's incoming node
                    # and mark this edge's outgoing node for removal
                    graph.add_edge(parent_edges[0][0], in_node,
                                   barcode=particle.barcode, particle=particle)
                    log.debug("Adding new edge %d -- %d with barcode %d",
                              parent_edges[0][0], in_node, particle.barcode)
                    remove_nodes.add(out_node)

                    break

        # Remove all redundant nodes, also removes the associated edges usefully
        log.debug("removing nodes %s" % remove_nodes)
        for node in remove_nodes:
            graph.remove_node(node)
