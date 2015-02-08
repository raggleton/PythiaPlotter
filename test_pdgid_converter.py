"""
Unit tests for pdgid_converter module
"""

import unittest
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doesn't work as doens't think it's a package
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pdgid_converter as pc
from pprint import pprint


class Checker_Test(unittest.TestCase):

    def test_particle_tex(self):
        self.assertEqual(pc.pdgid_to_tex(10511), "B_0^{*0}")
        self.assertEqual(pc.pdgid_to_tex(25), "h^0")

    def test_antiparticle_tex(self):
        self.assertEqual(pc.pdgid_to_tex(-23), "\overline{Z}^0") # neutral
        self.assertEqual(pc.pdgid_to_tex(-523), "B^{*-}")

    def test_particle_string(self):
        self.assertEqual(pc.pdgid_to_string(111), "pi0")

    def test_antiparticle_string(self):
        self.assertEqual(pc.pdgid_to_string(-111), "pi0")
        self.assertEqual(pc.pdgid_to_string(-323), "K*-")

    def test_wrong_pdgid(self):
        """Check it handles non-existing PDGIDs correctly"""
        self.assertRaises(KeyError, pc.pdgid_to_string, 9999)


def main():
    unittest.main()

if __name__ == '__main__':
    main()