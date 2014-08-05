"""
Prints relationships to GraphViz file when representing particles as nodes
(for edges see edgePrinter.py)
"""

import eventClasses
import config

config.VERBOSE = True

def printNodeToGraphViz(event, gvFilename, useRawNames=False):
    """Prints GenEvent to GraphViz file using particle inNode representation"""

    print "Writing GraphViz file to %s" % gvFilename
    with open(gvFilename, "w") as gvFile:
        # Now process the particles and add appropriate links to GraphViz file
        # Start from the end and work backwards to pick up all connections
        # (doesn't work if you start at beginning and follow daughters)
        gvFile.write("digraph g {\n    rankdir = RL;\n")

        # Set all initial particles to be level in diagram
        rank = "  {rank=same;"

        particles = event.particles
        for p in reversed(particles):

            if p.skip or p.name == "system":
                continue

            # Set DisplayAttributes as node
            p.displayAttributes.setAttributesForNode(
                interestingList=config.interesting,
                useRawName=useRawNames)

            entry = '    %s -> { ' % p.barcode

            for m in p.nodeAttributes.mothers:
                entry += '%s ' % m.barcode

            entry += "} [dir=\"back\"]\n"

            if not p.isInitialState:
                gvFile.write(entry)  # don't want p+ -> system entries
                if config.VERBOSE: print entry,
            else:
                rank += '%s ' % (p.barcode)

            # Write labels for text for each node (raw name or tex)
            # Set special features for initial/final state & interesting ones
            # Final state: box, yellow fill
            # Initial state: circle, green fill
            # Interesting: user-chosen colour fill, keep shape if initial/final
            # p.displayAttributes holds all this info
            nodeConfig = p.displayAttributes.getNodeString()
            gvFile.write(nodeConfig)
            if config.VERBOSE:
                print nodeConfig,

        rank += "} // Put initial particles on same level\n"
        if config.VERBOSE: print rank,
        gvFile.write(rank)
        gvFile.write("}")
        gvFile.write("")