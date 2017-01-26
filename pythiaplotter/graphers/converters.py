"""Functions to do conversions between particle representations."""


from __future__ import absolute_import
import logging
import pythiaplotter.utils.logging_config  # NOQA
import networkx as nx
from .node_grapher import assign_particles_nodes
from pythiaplotter.parsers.event_classes import NodeParticle


log = logging.getLogger(__name__)


def edge_to_node(graph):
    """Converts graph from edge to node representation.

    1) Create a node for each particle edge
    2) Add directed edges between all combinations of incoming & outgoing particles at a vertex

    Since there is a 1:1 correspondence between the node and edge particles,
    we can use the assign_particles_nodes() function to do this,
    so long as we construct our NodeParticles correctly.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    NetworkX.MultiDiGraph
    """
    node_particles = []
    for out_node, in_node, edge_data in graph.edges_iter(data=True):
        particle = edge_data['particle']
        parent_barcodes = [data['particle'].barcode for _, _, data
                           in graph.in_edges_iter(out_node, data=True)]
        np = NodeParticle(particle, parent_barcodes)
        node_particles.append(np)
    return assign_particles_nodes(node_particles)


def node_to_edge(graph):
    """Converts graph from node to edge representation.

    Harder.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph


    Returns
    -------
    NetworkX.MultiDiGraph
    """
    log.warning("node_to_edge not implemented!")
    return graph
