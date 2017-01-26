"""Attaches particles to a NetworkX graph, when NODES represent particles."""


from __future__ import absolute_import
import logging
import pythiaplotter.utils.logging_config  # NOQA
import networkx as nx


log = logging.getLogger(__name__)


def assign_particles_nodes(node_particles):
    """Attach Particles to a directed graph when NODES represent particles via NodeParticles.

    NodeParticle objects must have their parent_codes specified for this to work.

    It automatically attaches directed edges, between parent and child nodes.

    Parameters
    ----------
    node_particles : list[NodeParticle]
        List of NodeParticles, whose Particle's will be attached to a graph
        with the relationship specified by self.parent_codes.

    Returns
    -------
    NetworkX.MultiDiGraph
        Directed graph with particles assigned to nodes, and edges to represent relationships.
    """

    gr = nx.MultiDiGraph(attr=None)  # placeholder attr for later in printer

    # assign a node for each Particle obj
    for np in node_particles:
        gr.add_node(np.particle.barcode, particle=np.particle,
                    initial_state=False, final_state=False)

    # get the barcode of the system to avoid useless edges
    # and non-existent particles. 0 for Pythia8, -1 for CMSSW, but easiest
    # is to check in the list of nodes (since node barcode = particle barcode)
    system_barcode = -1 if 0 in gr.nodes() else 0

    # assign edges between Parents/Children
    for np in node_particles:
        if np.parent_codes:
            if np.parent_codes[0] == system_barcode and np.parent_codes[-1] == system_barcode:
                continue
            for i in np.parent_codes:
                gr.add_edge(i, np.particle.barcode)

    # Set initial_state and final_state flags, based on number of parents
    # (for initial_state) or number of children (for final_state)
    # This should be the only place it is done, otherwise confusing!
    for node, data in gr.nodes_iter(data=True):
        if len(gr.predecessors(node)) == 0:
            data['particle'].initial_state = True
            data['initial_state'] = True

        if len(gr.successors(node)) == 0:
            data['particle'].final_state = True
            data['final_state'] = True

    # log.debug("Graph nodes after assigning: %s" % gr.node)

    remove_isolated_nodes(gr)

    return gr


def remove_isolated_nodes(gr):
    """Remove nodes with no parents and no children.

    Parameters
    ----------
    gr : NetworkX.MultiDiGraph
    """
    nodes = gr.nodes()[:]
    for np in nodes:
        if len(gr.predecessors(np)) == 0 and len(gr.successors(np)) == 0:
            gr.remove_node(np)


def remove_redundant_nodes(graph):
    """Remove redundant particle nodes from a graph.

    i.e. when you have a particles which has 1 parent who has the same PDGID,
    and 1 child (no PDGID requirement).

    e.g.::

        ->-g->-g->-g->-

    These are useful to keep if considering Pythia8 internal workings,
    but otherwise are just confusing and a waste of space.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to remove redundant nodes from

    """
    for node, data in graph.nodes_iter(data=True):
        children = graph.successors(node)
        parents = graph.predecessors(node)
        if len(children) == 1 and len(parents) == 1:

            p = data['particle']
            parent = graph.node[parents[0]]['particle']
            child = graph.node[children[0]]['particle']
            if parent.pdgid == p.pdgid:
                # rewire the graph
                child.parent_codes = [parent.barcode]
                graph.remove_node(node)  # also removes the relevant edges
                graph.add_edge(parent.barcode, child.barcode)
