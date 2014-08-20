"""
Prints relationships to GraphViz file when representing particles as nodes
(for edges see edgeWriter.py)
"""

import eventClasses
import config


def printNodeToGraphViz(event, gvFilename, useRawNames=False):
    """Prints GenEvent to GraphViz file using particle in Node representation"""

    print "Writing GraphViz file to %s" % gvFilename
    with open(gvFilename, "w") as gvFile:
        # Now process the particles and add appropriate links to GraphViz file
        # Start from the end and work backwards to pick up all connections
        # (doesn't work if you start at beginning and follow daughters)
        gvFile.write("digraph g {\n    rankdir = RL;\n")

        for p in reversed(event.particles):

            if p.skip or p.name == "system":
                continue

            # Set DisplayAttributes as node
            p.display_attr.rawNames = useRawNames
            p.display_attr.setAttributesForNode(
                interestingList=CONFIG.interesting)

            entry = '    %s -> { ' % p.barcode

            for m in p.node_attr.mothers:
                entry += '%s ' % m.barcode

            entry += "} [dir=\"back\"]\n"

            if not p.isInitialState:
                gvFile.write(entry)  # don't want p+ -> system entries
                if CONFIG.VERBOSE:
                    print entry,

            # Write labels for each node
            nodeConfig = "    %s %s \n" % (p.barcode,
                                           p.display_attr.getNodeString())
            gvFile.write(nodeConfig)
            if CONFIG.VERBOSE:
                print nodeConfig,

        # Set all initial particles to be level in diagram
        rank = "  {rank=same;"
        rank += ' '.join([str(p.barcode) for p in event.particles
                          if p.isInitialState and p.pdgid != 90])
        rank += "} // Put initial particles on same level\n"
        if CONFIG.VERBOSE: print rank,
        gvFile.write(rank)

        gvFile.write("}")
        gvFile.write("")