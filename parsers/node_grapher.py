import networkx as nx


def assign_particles_nodes(particles, remove_redundants=True):
    """
    Attaches particles to a NetworkX directional graph,
    when NODES represent particles.

    It automatically attaches directed edges, from parent to child nodes.

    It also is possible to remove redundant nodes - i.e. when you have
    a particles who has 1 parent who has the same PDGID,
    and 1 child (no PDGID requirement)

    e.g.
    ->-g->-g->-g->-

    These are useful if considering how Pythia actually works,
    but otherwise are just confusing and waste space.
    """

    gr = nx.DiGraph()

    # assign a node for each Particle obj
    for particle in particles:
        gr.add_node(particle.barcode, particle=particle)

    # assign edges between Parent/Children
    # need to work backwards, since the Pythia daughter indices are
    # sometimes not complete, whereas mother IDs are
    for particle in reversed(particles):
        if particle.parent1_code == 0 and particle.parent2_code == 0:
            continue
        for i in xrange(particle.parent1_code, particle.parent2_code+1):
            gr.add_edge(i, particle.barcode)

    # store daughters properly, mark final state particles
    for node in gr.nodes():
        children = list(gr.successors(node))
        if children:
            gr.node[node]['particle'].child_codes = children
        else:
            gr.node[node]['particle'].final_state = True

    # remove redundant nodes from graph - NB they still exist in the Event tho...
    if remove_redundants:
        for node in gr.nodes():
            if (len(gr.successors(node)) == 1
               and len(gr.predecessors(node)) == 1):

                p = gr.node[node]['particle']
                parent = gr.node[gr.predecessors(node)[0]]['particle']
                child = gr.node[gr.successors(node)[0]]['particle']
                if parent.pdgid == p.pdgid:
                    # rewire the graph
                    parent.child_codes = p.child_codes
                    child.parent1_code = parent.barcode
                    child.parent2_code = parent.barcode
                    gr.remove_node(node)  # also removes the relevant edges
                    gr.add_edge(parent.barcode, child.barcode)

    return gr