"""
This file contains global definitions. Since there is only one instance of each
module, any changes made to the module object get reflected everywhere.
So can use for global variables e.g.

import config as CONFIG
...
if CONFIG.VERBOSE:
...

Robin Aggleton 22/7/14
"""

###########################
# USER EDIT THE FOLLOWING:
###########################

# Interesting particles we wish to highlight
# Can do different particles in different colours,
# see www.graphviz.org/doc/info/colors.html
# although requires xcolor latex package
# Relies on matching names though...better method?
# User must include antiparticles
interesting = [
    ["cyan", ["mu+", "mu-"]],
    ["blue", ["tau+", "tau-"]],
    ["red", ["b", "bbar"]],
    ["orange", ["c", "cbar"]],
    ["brown", ["s", "sbar"]]
]

# Color for initial particles (protons normally)
initial_color = "green"

# Color for final state particles
final_color = "purple"

#############################################################
# DO NOT EDIT BELOW HERE (unless you know what you're doing)
#############################################################

# Hide redundant particles - Pythia often does things like g -> g -> g -> g to
# represent some momentum shift or connection. Often, we don't care about that
# and just want an overview of what's going on.
# Also it means fewer particles to be drawn = less busy, faster to draw!
removeRedundants = True

# To print out intermediate lines during processing - only for debugging
VERBOSE = False
