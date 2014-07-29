"""
This file contains global definitions. In each python file definitions

import config

Since there is only one instance of each module, 
any changes made to the module object get reflected everywhere. 
So can use for global variables e.g.

config.VERBOSE

Robin Aggleton 22/7/14
"""

VERBOSE = False

removeRedundants = True

# Interesting particles we wish to highlight
# Can do different particles in different colours,
# see www.graphviz.org/doc/info/colors.html
# although requires xcolor latex package
# Relies on matching names though...better method?
# User must include antiparticles
# Make list in args?
interesting = [
              ["cyan", ["mu+", "mu-"]],
              ["blue", ["tau+", "tau-"]],
              ["red", ["b", "bbar"]],
              ["orange", ["c", "cbar"]],
              ["yellow", ["s", "sbar"]]
              ]