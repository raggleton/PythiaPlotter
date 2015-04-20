"""
Unit tests for RequisiteChecker class
"""

import unittest
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doesn't work as doens't think it's a package
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from utils.requisite_checker import RequisiteChecker
from pprint import pprint


class Checker_Test(unittest.TestCase):

    def setUp(self):
        self.real_prog = "vim"
        self.fake_prog = "fakeprog"
        self.real_mod = "argparse"
        self.fake_mod = "aaaaaaa"

        self.all_prog = [self.real_prog, self.fake_prog]
        self.all_mod = [self.real_mod, self.fake_mod]

        # Setup with 1 real program, 1 fake, 1 real module, 1 fake
        self.checkr = RequisiteChecker(programs=self.all_prog,
                                       modules=self.all_mod)
        pprint(self.checkr.results)

    def test_real_program(self):
        self.assertTrue(self.checkr.results[self.real_prog])

    def test_fake_program(self):
        self.assertFalse(self.checkr.results[self.fake_prog])

    def test_real_module(self):
        self.assertTrue(self.checkr.results[self.real_mod])

    def test_fake_module(self):
        self.assertFalse(self.checkr.results[self.fake_mod])


def main():
    unittest.main()

if __name__ == '__main__':
    main()