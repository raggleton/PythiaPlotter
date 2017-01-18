import pythiaplotter.utils.logging_config  # NOQA
import logging
import networkx as nx


log = logging.getLogger(__name__)


def assign_particles_nodes(node_particles, remove_redundants=True):
    """
    Attach particles to a NetworkX directed graph when NODES represent particles
    via NodeParticle objects.

    It automatically attaches directed edges, from parent to child nodes.
    """

    gr = nx.DiGraph()

    # assign a node for each Particle obj
    for np in node_particles:
        gr.add_node(np.particle.barcode, particle=np.particle,
                    initial_state=False, final_state=False)

    # get the barcode of the system to avoid useless edges
    # and non-existent particles. 0 for Pythia8, -1 for CMSSW, but easiest
    # is to check in the list of nodes (since node barcode = particle barcode)
    system_barcode = -1 if 0 in gr.nodes() else 0

    # assign edges between Parent/Children
    # need to work backwards, since the Pythia daughter indices are
    # sometimes not complete, whereas mother IDs are
    for np in reversed(node_particles):
        if np.parent1_code == system_barcode and np.parent2_code == system_barcode:
            continue
        for i in range(np.parent1_code, np.parent2_code + 1):
            gr.add_edge(i, np.particle.barcode)

    # Set initial_state and final_state flags, based on number of parents
    # (for initial_state) or number of children (for final_state)
    # This should be the only place it is done, otherwise confusing!
    for np in gr.nodes_iter():
        if len(gr.predecessors(np)) == 0:
            gr.node[np]['particle'].initial_state = True
            gr.node[np]['initial_state'] = True

        if len(gr.successors(np)) == 0:
            gr.node[np]['particle'].final_state = True
            gr.node[np]['final_state'] = True

    # log.debug("Graph nodes after assigning: %s" % gr.node)

    if remove_redundants:
        remove_redundant_nodes(gr)
        # log.debug("Graph nodes after remove_redundants: %s" % gr.node)

    return gr


def remove_redundant_nodes(graph):
    """
    Remove redundant particle nodes - i.e. when you have a particles which has
    1 parent who has the same PDGID, and 1 child (no PDGID requirement)

    e.g.
    ->-g->-g->-g->-

    These are useful to keep if considering Pythia8 internal workings,
    but otherwise are just confusing and a waste of space.
    """
    for node in graph.nodes():
        if (len(graph.successors(node)) == 1 and len(graph.predecessors(node)) == 1):

            p = graph.node[node]['particle']
            parent = graph.node[graph.predecessors(node)[0]]['particle']
            child = graph.node[graph.successors(node)[0]]['particle']
            if parent.pdgid == p.pdgid:
                # rewire the graph
                # parent.child_codes = p.child_codes
                child.parent1_code = parent.barcode
                child.parent2_code = parent.barcode
                graph.remove_node(node)  # also removes the relevant edges
                graph.add_edge(parent.barcode, child.barcode)
