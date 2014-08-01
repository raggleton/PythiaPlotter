#!/usr/bin/env python
"""
Unit test to test EdgeToNode conversion
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
import hepmcParser as h

class TestEdgeToNode(unittest.TestCase):

    def test_2to1_conversion(self):
        e = h.parse("test/testSamples/test_2to1.hepmc")
        mothersKnown = [1, 2]  # barcodes of mothers
        particle = e.particles[2]
        results = testParticleMothers(particle, mothersKnown)  # Get left over mothers
        self.failIf(results)

    def test_1to2_conversion(self):
        e = h.parse("test/testSamples/test_1to2.hepmc")
        mothersKnown = [1]  # barcodes of mothers
        particle2 = e.particles[1]
        results2 = testParticleMothers(particle2, mothersKnown)
        particle3 = e.particles[2]
        results3 = testParticleMothers(particle3, mothersKnown)
        self.failIf(results2 or results3)

    def test_3to1to2_conversion(self):
        """Test conversion with simple sample"""
        e = h.parse("test/testSamples/test_3to1to2.hepmc")
        mothers4 = [1, 2, 3]
        mothers5 = [4]
        particle4 = e.particles[3]
        particle5 = e.particles[4]
        particle6 = e.particles[5]
        results4 = testParticleMothers(particle4, mothers4)
        results5 = testParticleMothers(particle5, mothers5)
        results6 = testParticleMothers(particle6, mothers5)
        self.failIf(results4 or results5 or results6)

def testParticleMothers(particle, motherList):
    """Compare motherList to mothers of particle"""
    leftovers = []
    print "Particle barcode:", particle.barcode
    for m in particle.nodeAttributes.mothers:
        print "mother:", m.barcode
        if not m.barcode in motherList:
            leftovers.append(m)
            print "LEFTOVER: ", m.barcode
    return leftovers


def main():
    unittest.main()

if __name__ == '__main__':
    main()
