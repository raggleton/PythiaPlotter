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
            entry = '    {0:s} -> {1:s} {2:s}\n' \
                .format(
                str(p.edgeAttributes.outVertex.barcode).replace("-", "V"),
                str(p.edgeAttributes.inVertex.barcode).replace("-", "V"),
                p.displayAttributes.getEdgeString())

            gvFile.write(entry)
            if config.VERBOSE:
                print entry,

        # Print vertex display attributes, all the same for now
        for v in event.vertices:
            entry = '    %s [label="",shape=point, size=0.1]\n' % str(v.barcode).replace("-","V")
            gvFile.write(entry)
            if config.VERBOSE:
                print entry,

            # Set all initial vertices to be level in diagram
            # rank = "  {rank=same;"
            # rank += ' '.join([str(p.barcode) for p in event.particles
            #                   if p.isInitialState and p.pdgid != 90])
            # rank += "} // Put initial particles on same level\n"
            # if config.VERBOSE: print rank,
            # gvFile.write(rank)

        gvFile.write("}")
        gvFile.write("")