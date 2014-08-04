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
import pythiaParser as P
import config

class TestNodeToEdge(unittest.TestCase):

    config.VERBOSE = False

    # TODO: improve fail conditions - test that vertices and particles
    # have correct in/out barcodes

    def test_2to1_conversion_vertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_2to1.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.assertEqual(len(e.vertices), 3)

    def test_2to1_conversion_addFinalVertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_2to1.txt")
        print "number vertices before doing finals:", len(e.vertices)
        e.addVerticesForFinalState()
        print "number vertices after doing finals:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.assertEqual(len(e.vertices), 4)

    def test_1to2_conversion_vertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_1to2.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        [printParticle(part) for part in e.particles]
        self.assertEqual(len(e.vertices), 2)

    def test_1to2_conversion_addFinalVertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_1to2.txt")
        print "number vertices before doing finals:", len(e.vertices)
        e.addVerticesForFinalState()
        print "number vertices after doing finals:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.assertEqual(len(e.vertices), 4)

    def test_3to1to2_conversion_vertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_3to1to2.txt")
        print "number vertices:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.assertEqual(len(e.vertices), 5)

    def test_3to1to2_conversion_addFinalVertices(self):
        printTestHeader(self)
        e = P.parse("test/testSamples/test_3to1to2.txt")
        print "number vertices before doing finals:", len(e.vertices)
        e.addVerticesForFinalState()
        print "number vertices after doing finals:", len(e.vertices)
        [printVertex(v) for v in e.vertices]
        self.assertEqual(len(e.vertices), 7)

def printVertex(v):
    print "vtx barcode:", v.barcode, "num incoming:", len(v.inParticles), \
        "num outgoing:", len(v.outParticles)
    inBarcodes = [i.barcode for i in v.inParticles]
    outBarcodes = [i.barcode for i in v.outParticles]
    print "incoming barcodes", inBarcodes, "outgoing barcodes", outBarcodes

def printParticle(p):
    print ("p barcode:",p.barcode,
           "in vtx barcode:", p.edgeAttributes.inVertexBarcode,
           "out vtx barcode:", p.edgeAttributes.outVertexBarcode)

def printTestHeader(t):
    print "--------------------------------------------------------------------"
    print "Doing:", t.id()
    print ""

def main():
    unittest.main()

if __name__ == '__main__':
    main()
