"""
Unit tests for node_grapher
"""

import unittest
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doesn't work as doens't think it's a package
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import node_grapher as ng
from event_classes import Particle
from pprint import pprint


class NodeGrapher_Test(unittest.TestCase):

    verbose = True

    def setUp(self):
        pass

    def check_graph_nodes(self, particles, graph, verbose=verbose):
        """To test particles were correctly assigned to nodes"""
        node_particles = [graph.node[n]['particle'] for n in graph.nodes()]
        if verbose:
            print node_particles
            print graph.node
        return set(particles) == set(node_particles)

    def check_graph_edges(self, edges, graph, verbose=verbose):
        """To test edges were correctly assigned
        ATM just a simpler way to print info...
        """
        if verbose:
            print edges
            print graph.edges()
        return set(edges) == set(graph.edges())

    def test_1_to_2(self):
        """Very simple scenario: 1 particle decays to 2 daughters"""

        p1 = Particle(barcode="1", parent1="0", parent2="0")
        p2 = Particle(barcode="2", parent1="1", parent2="1")
        p3 = Particle(barcode="3", parent1="1", parent2="1")
        particles = [p1, p2, p3]
        g = ng.assign_particles_nodes(particles)
        self.assertTrue(self.check_graph_nodes(particles, g))
        edges = [('1','3'), ('1','2')]
        self.assertTrue(self.check_graph_edges(edges, g, False))

    def test_2_to_1_to_3(self):
        """2 particles (1,2) to 1 (3) to 3 (4,5,6)"""
        p1 = Particle(barcode="1", parent1="0", parent2="0", pdgid=11)
        p2 = Particle(barcode="2", parent1="0", parent2="0", pdgid=-11)
        p3 = Particle(barcode="3", parent1="1", parent2="2", pdgid=22)
        p4 = Particle(barcode="4", parent1="3", parent2="3", pdgid=11)
        p5 = Particle(barcode="5", parent1="3", parent2="3", pdgid=12)
        p6 = Particle(barcode="6", parent1="3", parent2="3", pdgid=13)
        particles = [p1, p2, p3, p4, p5, p6]
        g = ng.assign_particles_nodes(particles)
        self.assertTrue(self.check_graph_nodes(particles, g))
        edges = [('1','3'), ('2','3'), ('3','4'), ('3','5'), ('3','6')]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_redundant(self):
        """Check remove_redundants code.
        (1) to (2,3). Then (2)->(4)->(5), and (3) -> (5).
        So (4) should be redundant.
        """
        p1 = Particle(barcode="1", parent1="0", parent2="0", pdgid=11)
        p2 = Particle(barcode="2", parent1="1", parent2="1", pdgid=-11)
        p3 = Particle(barcode="3", parent1="1", parent2="1", pdgid=22)
        p4 = Particle(barcode="4", parent1="2", parent2="2", pdgid=-11)
        p5 = Particle(barcode="5", parent1="3", parent2="4", pdgid=12)
        particles = [p1, p2, p3, p4, p5]
        g = ng.assign_particles_nodes(particles)
        particles.remove(p4)
        self.assertTrue(self.check_graph_nodes(particles, g))
        edges = [('1','2'), ('1','3'), ('2','5'), ('3','5')]
        self.assertTrue(self.check_graph_edges(edges, g))

def main():
    unittest.main()

if __name__ == '__main__':
    main()