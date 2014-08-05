__author__ = 'robina'


"""Test nodeWriter.py"""

import unittest
import nodeWriter
import pythiaParser
import hepmcParser
import config
from common_test import printTestHeader
import os.path

class PrintNodeToGV(unittest.TestCase):

    def test_1to2(self):
        printTestHeader(self)
        parseAndPrintFile("test_1to2.txt")
        self.assertEqual(True, True)

    def test_2to1(self):
        printTestHeader(self)
        parseAndPrintFile("test_2to1.txt")
        self.assertEqual(True, True)

    def test_3to1to2(self):
        printTestHeader(self)
        parseAndPrintFile("test_3to1to2.txt")
        self.assertEqual(True, True)


def parseAndPrintFile(filename):
    e = pythiaParser.parse("test/testSamples/"+filename)
    postProcess(e)
    stemName = os.path.splitext(filename)[0]
    nodeWriter.printNodeToGraphViz(e, "test/testSamples/"+stemName+".gv",
                                        useRawNames=True)

def postProcess(e):
    """Do event post processing"""
    e.addVerticesForFinalState()

if __name__ == '__main__':
    unittest.main()
