__author__ = 'robina'

"""
Common functions for tests.
I guess this should really inherit from unittest,
then all my tests inherit from this
"""


def printTestHeader(t):
    print "--------------------------------------------------------------------"
    print "Doing:", t.id()
    print ""
