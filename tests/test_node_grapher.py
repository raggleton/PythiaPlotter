"""
Unit tests for node_grapher

"""


from __future__ import absolute_import
import unittest
import pythiaplotter.graphers.node_grapher as ng
from pythiaplotter.parsers.event_classes import Particle, NodeParticle
from pprint import pprint


class NodeGrapher_Test(unittest.TestCase):

    verbose = False

    def setUp(self):
        pass

    def check_graph_nodes(self, particles, graph, verbose=verbose):
        """To test particles were correctly assigned to nodes"""
        # print graph.nodes()
        node_particles = [graph.node[n]['particle'] for n in graph.nodes()]
        if verbose:
            print "User particles:"
            pprint(node_particles)
            print "Graph nodes:"
            print (graph.node)
        return set(particles) == set(node_particles)

    def check_graph_edges(self, edges, graph, verbose=verbose):
        """To test edges were correctly assigned
        ATM just a simpler way to print info...
        """
        if verbose:
            print "User edges:"
            pprint(edges)
            print "Graph edges:"
            pprint(graph.edges())
        return set(edges) == set(graph.edges())

    def test_1_to_2(self):
        """Very simple scenario: 1 particle decays to 2 daughters"""

        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=1),
                          parent1_barcode="0", parent2_barcode="0")
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=2),
                          parent1_barcode="1", parent2_barcode="1")
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=3),
                          parent1_barcode="1", parent2_barcode="1")
        particles = [p1, p2, p3]
        g = ng.assign_particles_nodes(particles)
        self.assertTrue(self.check_graph_nodes([p.particle for p in particles], g))
        edges = [(1, 3), (1, 2)]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_2_to_1_to_3(self):
        """2 particles (1,2) to 1 (3) to 3 (4,5,6)"""
        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=11),
                          parent1_barcode="0", parent2_barcode="0")
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=-11),
                          parent1_barcode="0", parent2_barcode="0")
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=22),
                          parent1_barcode="1", parent2_barcode="2")
        p4 = NodeParticle(particle=Particle(barcode=4, pdgid=11),
                          parent1_barcode="3", parent2_barcode="3")
        p5 = NodeParticle(particle=Particle(barcode=5, pdgid=12),
                          parent1_barcode="3", parent2_barcode="3")
        p6 = NodeParticle(particle=Particle(barcode=6, pdgid=13),
                          parent1_barcode="3", parent2_barcode="3")
        particles = [p1, p2, p3, p4, p5, p6]
        g = ng.assign_particles_nodes(particles)
        self.assertTrue(self.check_graph_nodes([p.particle for p in particles], g))
        edges = [(1, 3), (2, 3), (3, 4), (3, 5), (3, 6)]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_redundant(self):
        """Check remove_redundants code.
        (1) to (2,3). Then (2)->(4)->(5), and (3) -> (5).
        So (4) should be redundant.
        """
        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=11),
                          parent1_barcode="0", parent2_barcode="0")
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=-11),
                          parent1_barcode="1", parent2_barcode="1")
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=22),
                          parent1_barcode="1", parent2_barcode="1")
        p4 = NodeParticle(particle=Particle(barcode=4, pdgid=-11),
                          parent1_barcode="2", parent2_barcode="2")
        p5 = NodeParticle(particle=Particle(barcode=5, pdgid=12),
                          parent1_barcode="3", parent2_barcode="4")
        particles = [p1, p2, p3, p4, p5]
        g = ng.assign_particles_nodes(particles)
        particles.remove(p4)
        self.assertTrue(self.check_graph_nodes([p.particle for p in particles], g))
        edges = [(1, 2), (1, 3), (2, 5), (3, 5)]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_intial_final_state(self):
        """Test whether particles marked as initial/final state correctly

        (1)+(2) -> (3) -> (4),(5),(6)
        """
        p1 = NodeParticle(particle=Particle(barcode=1, pdgid=11),
                          parent1_barcode="0", parent2_barcode="0")
        p2 = NodeParticle(particle=Particle(barcode=2, pdgid=-11),
                          parent1_barcode="0", parent2_barcode="0")
        p3 = NodeParticle(particle=Particle(barcode=3, pdgid=22),
                          parent1_barcode="1", parent2_barcode="2")
        p4 = NodeParticle(particle=Particle(barcode=4, pdgid=11),
                          parent1_barcode="3", parent2_barcode="3")
        p5 = NodeParticle(particle=Particle(barcode=5, pdgid=12),
                          parent1_barcode="3", parent2_barcode="3")
        p6 = NodeParticle(particle=Particle(barcode=6, pdgid=13),
                          parent1_barcode="3", parent2_barcode="3")
        particles = [p1, p2, p3, p4, p5, p6]
        g = ng.assign_particles_nodes(particles)  # dummy var to hold graph
        self.assertTrue(p1.particle.initial_state)
        self.assertTrue(p2.particle.initial_state)
        self.assertTrue(p4.particle.final_state)
        self.assertTrue(p5.particle.final_state)
        self.assertTrue(p6.particle.final_state)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
