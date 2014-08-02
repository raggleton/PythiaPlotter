#!/usr/bin/env python
"""
Unit test to testNodeToEdge conversion
"""

import unittest
from pprint import pprint
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doens't work as doens't think it's a package
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import eventClasses as e
import pythiaParser as p
import config

class TestNodeToEdge(unittest.TestCase):

    config.VERBOSE = False

    def test_2to1_conversion_vertices(self):
        e = p.parse("test/testSamples/test_2to1.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.failUnless(len(e.vertices) == 3)

    # def test_2to1_conversion_particles(self):
    #     e = p.parse("test/testSamples/test_2to1.txt")
    #     daughtersKnown = [3]  # barcodes of daughters
    #     particle1 = e.particles[0]
    #     particle2 = e.particles[1]
    #     unmatched1 = testParticleDaughters(particle1, daughtersKnown)
    #     unmatched2 = testParticleDaughters(particle2, daughtersKnown)
    #     self.failIf(unmatched1 or unmatched2)

    def test_1to2_conversion_vertices(self):
        e = p.parse("test/testSamples/test_1to2.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.failUnless(len(e.vertices) == 2)
    #
    # def test_1to2_conversion_daughters(self):
    #     e = p.parse("test/testSamples/test_1to2.txt")
    #     daughtersKnown = [2, 3]  # barcodes of daughters
    #     particle = e.particles[0]
    #     unmatched = testParticleDaughters(particle, daughtersKnown)
    #     self.failIf(unmatched)
    #
    def test_3to1to2_conversion_vertices(self):
        e = p.parse("test/testSamples/test_3to1to2.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.failUnless(len(e.vertices) == 5)
    #
    # def test_3to1to2_conversion_daughters(self):
    #     """Test conversion with simple sample"""
    #     e = p.parse("test/testSamples/test_3to1to2.txt")
    #     daughters1 = [4]
    #     daughters4 = [5, 6]
    #     particle1 = e.particles[0]
    #     particle2 = e.particles[1]
    #     particle3 = e.particles[2]
    #     particle4 = e.particles[3]
    #     unmatched1 = testParticleDaughters(particle1, daughters1)
    #     unmatched2 = testParticleDaughters(particle2, daughters1)
    #     unmatched3 = testParticleDaughters(particle3, daughters1)
    #     unmatched4 = testParticleDaughters(particle4, daughters4)
    #     self.failIf(unmatched4 or unmatched1 or unmatched2 or unmatched3)


def testParticleMothers(particle, motherList):
    """Compare motherList to mothers of particle"""
    print ("Particle barcode:", particle.barcode,
           len(particle.nodeAttributes.mothers), "mothers")
    mums = [m.barcode for m in particle.nodeAttributes.mothers]
    print mums
    leftovers = set(motherList).difference(set(mums))
    if leftovers:
        print "LEFTOVER:", leftovers
    return leftovers


def testParticleDaughters(particle, daughterList):
    """Compare daughterList to daughters of particle"""
    print ("Particle barcode:", particle.barcode,
           len(particle.nodeAttributes.daughters), "daughters")
    daughters = [m.barcode for m in particle.nodeAttributes.daughters]
    print daughters
    leftovers = set(daughterList).difference(set(daughters))
    if leftovers:
        print "LEFTOVER:", leftovers
    return leftovers


def printVertex(v):
    print "vtx barcode:", v.barcode, "num incoming:", len(v.inParticles), "num outgoing:", len(v.outParticles)
    inBarcodes = [i.barcode for i in v.inParticles]
    outBarcodes = [i.barcode for i in v.outParticles]
    print "incoming barcodes", inBarcodes, "outgoing barcodes", outBarcodes


def main():
    unittest.main()

if __name__ == '__main__':
    main()
