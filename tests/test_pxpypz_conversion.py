"""Tests for px/py/pz -> pt/eta/phi conversion"""


from __future__ import absolute_import, division, print_function
import unittest
import math
from pythiaplotter.parsers.event_classes import convert_px_py_pz


class Converter_Test(unittest.TestCase):

    def test_px(self):
        pt, eta, phi = convert_px_py_pz(1, 0, 0)
        self.assertTrue(pt == 1)
        self.assertTrue(phi == 0)
        self.assertTrue(eta == 0)

    def test_px_neg(self):
        pt, eta, phi = convert_px_py_pz(-1, 0, 0)
        self.assertTrue(pt == 1)
        self.assertTrue(phi == 0)
        self.assertTrue(eta == 0)

    def test_py(self):
        pt, eta, phi = convert_px_py_pz(0, 1, 0)
        self.assertEqual(pt, 1)
        self.assertAlmostEqual(phi, math.pi/2)
        self.assertEqual(eta, 0)

    def test_py_neg(self):
        pt, eta, phi = convert_px_py_pz(0, -1, 0)
        self.assertEqual(pt, 1)
        self.assertAlmostEqual(phi, -math.pi/2)
        self.assertEqual(eta, 0)

    def test_pz(self):
        pt, eta, phi = convert_px_py_pz(0, 0, 1)
        self.assertEqual(pt, 0)
        self.assertEqual(phi, 0)
        self.assertEqual(eta, float('inf'))

    def test_pz_neg(self):
        pt, eta, phi = convert_px_py_pz(0, 0, -1)
        self.assertEqual(pt, 0)
        self.assertEqual(phi, 0)
        self.assertEqual(eta, -float('inf'))

    def test_pxpy(self):
        pt, eta, phi = convert_px_py_pz(1, 1, 0)
        self.assertEqual(pt, math.sqrt(2))
        self.assertAlmostEqual(phi, math.pi/4)
        self.assertEqual(eta, 0)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
