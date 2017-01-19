"""
Unit tests for edge_grapher

"""


from __future__ import absolute_import
import unittest
import sys
import os.path
import pythiaplotter.graphers.edge_grapher as eg
from pythiaplotter.parsers.event_classes import Particle, EdgeParticle
from pprint import pprint


class EdgeGrapher_Test(unittest.TestCase):

    verbose = False

    def setUp(self):
        pass

    def check_graph_particles(self, particles, graph, verbose=verbose):
        """To test particles were correctly assigned to edges"""
        edge_particles = [graph.edge[i][j]['particle'] for i, j in graph.edges()]
        if verbose:
            print "User particles:"
            pprint(set(particles))
            print "Graph edge particles:"
            pprint(set(edge_particles))
        return set(particles) == set(edge_particles)

    def check_graph_edges(self, edges, graph, verbose=verbose):
        """To test edges were correctly assigned"""
        edges = [(int(i), int(j)) for i, j in edges]
        if verbose:
            print "User edges:",
            pprint(set(edges))
            print "Graph edges:"
            pprint(set(graph.edges()))
        return set(edges) == set(graph.edges())

    def test_1_to_2(self):
        """Very simple scenario: 1 particle decays to 2 daughters

        (0) - p1 -> (1) (1) - p2 -> (2)
                        (1) - p3 -> (3)

        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=11),
                          vtx_out_barcode="0", vtx_in_barcode="1")
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=11),
                          vtx_out_barcode="1", vtx_in_barcode="2")
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=11),
                          vtx_out_barcode="1", vtx_in_barcode="3")
        particles = [p1, p2, p3]
        g = eg.assign_particles_edges(particles, remove_redundants=False)
        self.assertTrue(self.check_graph_particles([p.particle for p in particles], g))
        edges = [(0, 1), (1, 3), (1, 2)]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_2_to_1_to_3(self):
        """2 particles to 1 to 3

        (0) - p1 -> (2) (2) - p3 -> (3) (3) - p4 -> (4)
        (1) - p2 -> (2)                 (3) - p5 -> (5)
                                        (3) - p6 -> (6)
        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=11),
                          vtx_out_barcode=0, vtx_in_barcode=2)
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=-11),
                          vtx_out_barcode=1, vtx_in_barcode=2)
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=22),
                          vtx_out_barcode=2, vtx_in_barcode=3)
        p4 = EdgeParticle(particle=Particle(barcode=4, pdgid=11),
                          vtx_out_barcode=3, vtx_in_barcode=4)
        p5 = EdgeParticle(particle=Particle(barcode=5, pdgid=12),
                          vtx_out_barcode=3, vtx_in_barcode=5)
        p6 = EdgeParticle(particle=Particle(barcode=6, pdgid=13),
                          vtx_out_barcode=3, vtx_in_barcode=6)
        particles = [p1, p2, p3, p4, p5, p6]
        g = eg.assign_particles_edges(particles, remove_redundants=False)
        self.assertTrue(self.check_graph_particles([p.particle for p in particles], g))
        edges = [(0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (3, 6)]
        self.assertTrue(self.check_graph_edges(edges, g))

    def test_redundant_simple(self):
        """Check remove_redundants code with a very simple case.

        (i) is node i, pj is edge/particle j

        (-1)--p1(u)--(-2)--p3(u)--(-3)--p4(u)--(-5)--p5(u)--(-6)--p6(u)--(-7)
                       |                                      |
                     (-2)--p2(g)--(-4)                      (-6)--p7(g)--(-8)

        should simplify to

        (-1)--p1(u)--(-2)----p3(u)----(-6)----p6(u)----(-7)
                       |                |
                     (-2)--p2(g)--(-4)  |
                                      (-6)--p7(g)--(-8)

        since p4 and p5 have the same pdgid as p3 and are therefore redundant
        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=2),
                          vtx_out_barcode=-1, vtx_in_barcode=-2)
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=22),
                          vtx_out_barcode=-2, vtx_in_barcode=-4)
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=2),
                          vtx_out_barcode=-2, vtx_in_barcode=-3)
        p4 = EdgeParticle(particle=Particle(barcode=4, pdgid=2),
                          vtx_out_barcode=-3, vtx_in_barcode=-5)
        p5 = EdgeParticle(particle=Particle(barcode=5, pdgid=2),
                          vtx_out_barcode=-5, vtx_in_barcode=-6)
        p6 = EdgeParticle(particle=Particle(barcode=6, pdgid=2),
                          vtx_out_barcode=-6, vtx_in_barcode=-7)
        p7 = EdgeParticle(particle=Particle(barcode=7, pdgid=22),
                          vtx_out_barcode=-6, vtx_in_barcode=-8)
        particles = [p1, p2, p3, p4, p5, p6, p7]
        graph = eg.assign_particles_edges(particles, remove_redundants=True)
        edges = [(-1, -2), (-2, -4), (-2, -6), (-6, -7), (-6, -8)]
        self.assertTrue(self.check_graph_edges(edges, graph))

    def test_intial_final_state(self):
        """Test whether particles marked as initial/final state correctly

        Uses the 2 particles to 1 to 3 setup

        (0) - p1 -> (2) (2) - p3 -> (3) (3) - p4 -> (4)
        (1) - p2 -> (2)                 (3) - p5 -> (5)
                                        (3) - p6 -> (6)
        """
        p1 = EdgeParticle(particle=Particle(barcode=1, pdgid=11),
                          vtx_out_barcode=0, vtx_in_barcode=2)
        p2 = EdgeParticle(particle=Particle(barcode=2, pdgid=-11),
                          vtx_out_barcode=1, vtx_in_barcode=2)
        p3 = EdgeParticle(particle=Particle(barcode=3, pdgid=22),
                          vtx_out_barcode=2, vtx_in_barcode=3)
        p4 = EdgeParticle(particle=Particle(barcode=4, pdgid=11),
                          vtx_out_barcode=3, vtx_in_barcode=4)
        p5 = EdgeParticle(particle=Particle(barcode=5, pdgid=12),
                          vtx_out_barcode=3, vtx_in_barcode=5)
        p6 = EdgeParticle(particle=Particle(barcode=6, pdgid=13),
                          vtx_out_barcode=3, vtx_in_barcode=6)
        particles = [p1, p2, p3, p4, p5, p6]
        g = eg.assign_particles_edges(particles, remove_redundants=False)
        self.assertTrue(p1.particle.initial_state)
        self.assertTrue(p2.particle.initial_state)
        self.assertTrue(p4.particle.final_state)
        self.assertTrue(p5.particle.final_state)
        self.assertTrue(p6.particle.final_state)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
