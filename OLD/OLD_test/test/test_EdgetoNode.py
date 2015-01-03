#!/usr/bin/env python
"""
Unit test to test EdgeToNode conversion
"""

import unittest
from pprint import pprint
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doesn't work as doesn't think it's a package
# OR run it from the main dir, not test/
# import sys
# import os.path
# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import eventClasses as e
import hepmcParser as h
from common_test import printTestHeader


class TestEdgeToNode(unittest.TestCase):

    def test_2to1_conversion_mothers(self):
        printTestHeader(self)
        e = h.parse("test/testSamples/test_2to1.hepmc")
        mothersKnown = [1, 2]  # barcodes of mothers
        particle = e.getParticle(3)
        # Get left over mothers
        unmatched = testParticleMothers(particle, mothersKnown)
        self.failIf(unmatched)

    def test_2to1_conversion_daughters(self):
        printTestHeader(self)
        e = h.parse("test/testSamples/test_2to1.hepmc")
        daughtersKnown = [3]  # barcodes of daughters
        particle1 = e.getParticle(1)
        particle2 = e.getParticle(2)
        unmatched1 = testParticleDaughters(particle1, daughtersKnown)
        unmatched2 = testParticleDaughters(particle2, daughtersKnown)
        self.failIf(unmatched1 or unmatched2)

    def test_1to2_conversion_mothers(self):
        printTestHeader(self)
        e = h.parse("test/testSamples/test_1to2.hepmc")
        mothersKnown = [1]  # barcodes of mothers
        particle2 = e.getParticle(2)
        unmatched2 = testParticleMothers(particle2, mothersKnown)
        particle3 = e.getParticle(3)
        unmatched3 = testParticleMothers(particle3, mothersKnown)
        self.failIf(unmatched2 or unmatched3)

    def test_1to2_conversion_daughters(self):
        printTestHeader(self)
        e = h.parse("test/testSamples/test_1to2.hepmc")
        daughtersKnown = [2, 3]  # barcodes of daughters
        particle = e.getParticle(1)
        unmatched = testParticleDaughters(particle, daughtersKnown)
        self.failIf(unmatched)

    def test_3to1to2_conversion_mothers(self):
        """Test conversion with simple sample"""
        printTestHeader(self)
        e = h.parse("test/testSamples/test_3to1to2.hepmc")
        mothers4 = [1, 2, 3]
        mothers5 = [4]
        particle4 = e.getParticle(4)
        particle5 = e.getParticle(5)
        particle6 = e.getParticle(6)
        unmatched4 = testParticleMothers(particle4, mothers4)
        unmatched5 = testParticleMothers(particle5, mothers5)
        unmatched6 = testParticleMothers(particle6, mothers5)
        self.failIf(unmatched4 or unmatched5 or unmatched6)

    def test_3to1to2_conversion_daughters(self):
        """Test conversion with simple sample"""
        printTestHeader(self)
        e = h.parse("test/testSamples/test_3to1to2.hepmc")
        daughters1 = [4]
        daughters4 = [5, 6]
        particle1 = e.getParticle(1)
        particle2 = e.getParticle(2)
        particle3 = e.getParticle(3)
        particle4 = e.getParticle(4)
        unmatched1 = testParticleDaughters(particle1, daughters1)
        unmatched2 = testParticleDaughters(particle2, daughters1)
        unmatched3 = testParticleDaughters(particle3, daughters1)
        unmatched4 = testParticleDaughters(particle4, daughters4)
        self.failIf(unmatched4 or unmatched1 or unmatched2 or unmatched3)


def testParticleMothers(particle, motherList):
    """Compare motherList to mothers of particle"""
    print ("Particle barcode:", particle.barcode,
           len(particle.node_attr.mothers), "mothers")
    mums = [m.barcode for m in particle.node_attr.mothers]
    print mums
    leftovers = set(motherList).difference(set(mums))
    if leftovers:
        print "LEFTOVER:", leftovers
    return leftovers


def testParticleDaughters(particle, daughterList):
    """Compare daughterList to daughters of particle"""
    print ("Particle barcode:", particle.barcode,
           len(particle.node_attr.daughters), "daughters")
    daughters = [m.barcode for m in particle.node_attr.daughters]
    print daughters
    leftovers = set(daughterList).difference(set(daughters))
    if leftovers:
        print "LEFTOVER:", leftovers
    return leftovers

def main():
    unittest.main()

if __name__ == '__main__':
    main()
