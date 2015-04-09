"""
Attaches particles etc to a NetworkX graph, when EDGES represent particles.
"""


import networkx as nx


def assign_particles_edges(particles, remove_redundants=True):
    gr = nx.DiGraph()

    # assign a node for each Particle obj
    for particle in particles:
        # gr.add_edge(particle.barcode, particle=particle)
