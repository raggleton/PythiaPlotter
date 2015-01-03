"""To test pythiaParser methods"""

__author__ = 'robina'

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

import eventClasses as E
import pythiaParser as P
import config

class TestPythiaParser(unittest.TestCase):

    def test_1to2(self):
        e = P.parse("test/testSamples/test_1to2.txt")
        self.assertEqual(True, False)


def printParticle(p)
    print ("barcode:", p.barcode, "mother1 barcode:", )

if __name__ == '__main__':
    unittest.main()
