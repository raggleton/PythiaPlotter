import utils.logging_config
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
        gr.add_node(np.particle.barcode, particle=np.particle)

    # assign edges between Parent/Children
    # need to work backwards, since the Pythia daughter indices are
    # sometimes not complete, whereas mother IDs are
    for np in reversed(node_particles):
        if np.parent1_code == 0 and np.parent2_code == 0:
            continue
        for i in xrange(np.parent1_code, np.parent2_code + 1):
            gr.add_edge(i, np.particle.barcode)

    # store daughters properly, mark final state particles
    for node in gr.nodes():
        children = list(gr.successors(node))
        if not children:
            gr.node[node]['particle'].final_state = True
            # gr.node[node]['particle'].child_codes = children
        # mark node as initial state or not, so we can align them on graph
        gr.node[node]['initial_state'] = gr.node[node]['particle'].initial_state

    # remove redundant nodes from graph - NB they still exist in the Event tho
    if remove_redundants:
        remove_redundant_nodes(gr)

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
        if (len(graph.successors(node)) == 1
           and len(graph.predecessors(node)) == 1):

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