"""
Prints relationships to GraphViz file when representing particles as nodes
(for edges see edgePrinter.py)
"""

import eventClasses
import config



def printEdgeToGraphViz(event, gvFilename, useRawNames=False):
    """Prints GenEvent to GraphViz file using particle in Edge representation"""
    config.VERBOSE = True

    print "Writing GraphViz file to %s" % gvFilename
    with open(gvFilename, "w") as gvFile:
        # Now process the particles and add appropriate links to GraphViz file
        gvFile.write("digraph g {\n    rankdir = LR;\n")

        for p in event.particles:

            # if p.skip or p.name == "system":
            #     continue

            p.displayAttributes.setAttributesForNode(
                interestingList=config.interesting, useRawName=useRawNames)

            # Do particle line from vertex to vertex
            entry = '    {0:s} -> {1:s} {2:s}\n'.format(
                p.edgeAttributes.outVertex.barcode,
                p.edgeAttributes.inVertex.barcode,
                p.displayAttributes.getEdgeString())

            gvFile.write(entry)
            if config.VERBOSE:
                print entry,

        # Print vertex display attributes, all the same for now
        for v in event.vertices:
            color = "black"
            if v.isInitialState or v.isFinalState:
                color = "transparent"

            entry = '    %s [label="",shape=point, size=0.1, color=%s]\n' \
                    % (str(v.barcode).replace("-", "V"), color)
            gvFile.write(entry)
            if config.VERBOSE:
                print entry,

        # Set all initial vertices to be level in diagram
        rank = "  {rank=same;"
        initial = [p.edgeAttributes.outVertexBarcode for p in event.particles
                   if p.isInitialState]
        rank += ' '.join(initial)
        rank += "} // Put initial particles on same level\n"
        if config.VERBOSE: print rank,
        # gvFile.write(rank)

        gvFile.write("}")
        gvFile.write("")