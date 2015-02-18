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
# -> For non-TeX mode, use the list:
# www.graphviz.org/doc/info/colors.html
# -> For TeX mode, requires xcolor latex package 
# AND put in CamelCase to ensure it works with TikZ)
# AND you have to choose from Section 4.4 of 
# http://anorien.csc.warwick.ac.uk/mirrors/CTAN/macros/latex/contrib/xcolor/xcolor.pdf
# Probably a good idea to pick ones that apear in both lists
# 
# You need to define a list where each entry is a list with the form:
# [ <colour>, [<list of particles>]]
# where list of particles can either be their names,
# or their PDGIDs (see example below).
# Note, you have to add in antiparticles as well, if you want them highlighted.
interesting = [
    ["Purple1", [13,-13,11,-11]],
    # ["blue", ["tau+", "tau-"]],
    # ["red", ["b", "bbar"]],
    # ["Orange1", ["c", "cbar"]],
    # ["Chocolate3", [3, -3]]
    ["red", [12,-12,14,-14,16,-16]]
]

# Color for initial particles (protons normally)
initial_color = "Green3"

# Color for final state particles
final_color = "SteelBlue2"

#############################################################
# DO NOT EDIT BELOW HERE (unless you know what you're doing)
#############################################################

# Hide redundant particles - Pythia often does things like g -> g -> g -> g to
# represent some momentum shift or connection. Often, we don't care about that
# and just want an overview of what's going on.
# Also it means fewer particles to be drawn = less busy, faster to draw!
removeRedundants = False

# To print out intermediate lines during processing - only for debugging
VERBOSE = False

# Store user args globally so everyone can access them
# Or should I be passing as argument to classes - could get tedious?
args = None