#!/usr/bin/env python
"""
Unit test to test Units class
"""

import unittest
# To import from directory above test/
# Doing:
# from .. import eventclasses
# doens't work as doens't think it's a package
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import eventClasses as e


class TestUnits(unittest.TestCase):

    def test_Units_normal_input(self):
        """Test normal functionality"""
        u = e.Units(momentumUnit="MEV", positionUnit="CM")
        self.failUnless(u.momentumUnit == "MEV" and u.positionUnit == "CM")

    def test_Units_stupid_input(self):
        """Test what happens when you get odd input"""
        u = e.Units(momentumUnit="ASD", positionUnit=1)
        self.failUnless(u.momentumUnit == "GEV" and u.positionUnit == "MM")

    def test_Units_defaults(self):
        """Test defaults work"""
        u = e.Units()
        self.failUnless(u.momentumUnit == "GEV" and u.positionUnit == "MM")

def main():
    unittest.main()

if __name__ == '__main__':
    main()
