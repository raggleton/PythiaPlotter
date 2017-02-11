"""Functions to assign particles to a graph, and converting between node & edge representations."""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.graphers.edge_grapher import assign_particles_edges, remove_redundant_edges
from pythiaplotter.graphers.node_grapher import assign_particles_nodes, remove_redundant_nodes
from pythiaplotter.utils.common import check_representation_str
from pythiaplotter.graphers.converters import node_to_edge, edge_to_node


log = get_logger(__name__)


def assign_particles_to_graph(particles, default_repr, desired_repr=None, remove_redundants=True):
    """Wrapper to easily assign particles to graph, change representation, remove redundants.

    Parameters
    ----------
    particles : list[NodeParticle], list[EdgeParticle]
        List of particles to be assigned to a graph. Must include relationship information.
    default_repr : {"NODE", "EDGE"}
        Particle representation for particles
    desired_repr : {"NODE", "EDGE"}, optional
        Desired output representation.
    remove_redundants : bool, optional
        Whether to remove redundant particles from the graph.

    Returns
    -------
    NetworkX.MultiDiGraph
    """
    check_representation_str(default_repr, "default_repr")
    if default_repr == "NODE":
        graph = assign_particles_nodes(particles)
    elif default_repr == "EDGE":
        graph = assign_particles_edges(particles)
        remove_edges_by_pdgid(graph, 22, True)

    new_repr = default_repr

    if desired_repr and desired_repr != default_repr:
        check_representation_str(desired_repr, "desired_repr")

        new_repr = desired_repr
        if (default_repr, desired_repr) == ("NODE", "EDGE"):
            graph = node_to_edge(graph)
        elif (default_repr, desired_repr) == ("EDGE", "NODE"):
            graph = edge_to_node(graph)

    if remove_redundants:
        if new_repr == "NODE":
            remove_redundant_nodes(graph)
        elif new_repr == "EDGE":
            remove_redundant_edges(graph)

    return graph
