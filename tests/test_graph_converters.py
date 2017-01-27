"""Tests for graph converter functions"""


from __future__ import absolute_import, print_function
import logging
import pythiaplotter.utils.logging_config  # NOQA
import unittest
from pprint import pprint
import pytest
from pythiaplotter.parsers.event_classes import Particle, EdgeParticle, NodeParticle
from pythiaplotter.graphers.converters import node_to_edge, edge_to_node, \
    get_related_parents_children, duplication_needed
from pythiaplotter.graphers.edge_grapher import assign_particles_edges
from pythiaplotter.graphers.node_grapher import assign_particles_nodes
import networkx as nx


log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


class Converter_Tests(unittest.TestCase):

    verbose = False

    def compare_lists(self, thing, other):
        self.assertEqual(sorted(thing), sorted(other))

    def check_graph_node_particles(self, particles, graph):
        """To test particles were correctly assigned to nodes"""
        node_particles = [data['particle'] for _, data in graph.nodes_iter(data=True)]
        if self.verbose:
            print("User particles:")
            pprint(node_particles)
            print("Graph nodes:")
            print (graph.node)
        self.compare_lists(particles, node_particles)

    def check_graph_edge_particles(self, particles, graph):
        """To test particles were correctly assigned to edges"""
        edge_particles = [data['particle'] for _, _, data in graph.edges_iter(data=True)]
        if self.verbose:
            print("User particles:")
            pprint(particles)
            print("Graph edge particles:")
            pprint(edge_particles)
        self.compare_lists(particles, edge_particles)

    def check_graph_edges(self, edges, graph):
        """To test edges were correctly assigned
        ATM just a simpler way to print info...
        """
        if self.verbose:
            print("User edges:")
            pprint(edges)
            print("Graph edges:")
            pprint(graph.edges())
        self.compare_lists(edges, graph.edges())

    def test_1_to_2_edge_to_node(self):
        """Very simple scenario: 1 particle decays to 2 daughters

        (0) - p1 -> (1) (1) - p2 -> (2)
                        (1) - p3 -> (3)

        becomes

        p1 ->- p2
            |- p3

        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=11),
                          vtx_out_barcode="0", vtx_in_barcode="1")
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=12),
                          vtx_out_barcode="1", vtx_in_barcode="2")
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=13),
                          vtx_out_barcode="1", vtx_in_barcode="3")
        particles = [p1, p2, p3]
        g_edge = assign_particles_edges(particles)
        g_node = edge_to_node(g_edge)

        n1 = Particle(barcode=1, pdgid=11)
        n2 = Particle(barcode=2, pdgid=12)
        n3 = Particle(barcode=3, pdgid=13)
        n_particles = [n1, n2, n3]
        log.debug(vars(g_node))
        ideal_edges = [(1, 3), (1, 2)]
        self.check_graph_edges(ideal_edges, g_node)
        self.check_graph_node_particles(n_particles, g_node)

    def test_2_to_1_to_3_edge_to_node(self):
        """2 particles to 1 to 3

        (0) - p1 -> (2) (2) - p3 -> (3) (3) - p4 -> (4)
        (1) - p2 -> (2)                 (3) - p5 -> (5)
                                        (3) - p6 -> (6)

        becomes

        p1 ->- p3 ->- p4
        p2 -|      |- p5
                   |- p6
        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=11),
                          vtx_out_barcode=0, vtx_in_barcode=2)
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=12),
                          vtx_out_barcode=1, vtx_in_barcode=2)
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=13),
                          vtx_out_barcode=2, vtx_in_barcode=3)
        p4 = EdgeParticle(particle=Particle(barcode=4, pdgid=14),
                          vtx_out_barcode=3, vtx_in_barcode=4)
        p5 = EdgeParticle(particle=Particle(barcode=5, pdgid=15),
                          vtx_out_barcode=3, vtx_in_barcode=5)
        p6 = EdgeParticle(particle=Particle(barcode=6, pdgid=16),
                          vtx_out_barcode=3, vtx_in_barcode=6)
        particles = [p1, p2, p3, p4, p5, p6]
        g_edge = assign_particles_edges(particles)
        g_node = edge_to_node(g_edge)
        n1 = Particle(barcode=1, pdgid=11)
        n2 = Particle(barcode=2, pdgid=12)
        n3 = Particle(barcode=3, pdgid=13)
        n4 = Particle(barcode=4, pdgid=14)
        n5 = Particle(barcode=5, pdgid=15)
        n6 = Particle(barcode=6, pdgid=16)
        self.check_graph_node_particles([n1, n2, n3, n4, n5, n6], g_node)
        ideal_edges = [(1, 3), (2, 3), (3, 4), (3, 5), (3, 6)]
        self.check_graph_edges(ideal_edges, g_node)

    def test_1_to_2_node_to_edge(self):
        """Simple graph that does not require duplicate nodes."""
        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=1),
                          parent_barcodes=[])
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=2),
                          parent_barcodes=[1])
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=3),
                          parent_barcodes=[1])
        particles = [p1, p2, p3]
        g_node = assign_particles_nodes(particles)
        g_edge = node_to_edge(g_node)
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=1),
                          vtx_out_barcode=0, vtx_in_barcode=1)
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=2),
                          vtx_out_barcode=1, vtx_in_barcode=2)
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=3),
                          vtx_out_barcode=1, vtx_in_barcode=3)
        self.check_graph_edge_particles([p1.particle, p2.particle, p3.particle], g_edge)
        self.check_graph_edges([(0, 1), (1, 2), (1, 3)], g_edge)

    def test_2_to_3_node_to_edge(self):
        """Simple graph structure that requires duplicate nodes"""
        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=1),
                          parent_barcodes=[])
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=2),
                          parent_barcodes=[])
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=3),
                          parent_barcodes=[1])
        p4 = NodeParticle(particle=Particle(barcode=4, pdgid=4),
                          parent_barcodes=[1, 2])
        p5 = NodeParticle(particle=Particle(barcode=5, pdgid=5),
                          parent_barcodes=[2])
        particles = [p1, p2, p3, p4, p5]
        g_node = assign_particles_nodes(particles)
        g_edge = node_to_edge(g_node)
        self.check_graph_edges([(0, 1), (1, 4), (1, 5), (5, 6), (3, 7), (2, 3), (3, 5)], g_edge)
        new1 = Particle(barcode=20001, pdgid=1)
        new2 = Particle(barcode=20002, pdgid=2)
        self.check_graph_edge_particles([p1.particle, p2.particle, p3.particle, p4.particle,
                                         p5.particle, new1, new2], g_edge)

    def test_subgraph_finder(self):
        """Test the parent/children subgraph finder"""
        g = nx.MultiDiGraph()
        g.add_edges_from([(1, 2), (2, 3), (1, 4), (4, 5), (4, 7), (6, 7)])
        parents, children = get_related_parents_children(g, 1)
        self.compare_lists(parents, [1])
        self.compare_lists(children, [2, 4])
        parents, children = get_related_parents_children(g, 2)
        self.compare_lists(parents, [2])
        self.compare_lists(children, [3])
        parents, children = get_related_parents_children(g, 4)
        self.compare_lists(parents, [4, 6])
        self.compare_lists(children, [5, 7])
        parents, children = get_related_parents_children(g, 6)
        self.compare_lists(parents, [4, 6])
        self.compare_lists(children, [5, 7])

    def test_duplicates_needed(self):
        """Test whether duplicate particles needed"""
        g = nx.MultiDiGraph()
        g.add_edges_from([(1, 2), (2, 3), (1, 4), (4, 5), (4, 7), (6, 7)])
        parents, children = get_related_parents_children(g, 1)
        self.assertFalse(duplication_needed(g, parents, children))
        parents, children = get_related_parents_children(g, 4)
        self.assertTrue(duplication_needed(g, parents, children))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
