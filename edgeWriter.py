"""
Prints relationships to GraphViz file when representing particles as nodes
(for edges see edgePrinter.py)
"""

import eventClasses
import config as CONFIG


def printEdgeToGraphViz(event, gvFilename, useRawNames=False):
    """Prints GenEvent to GraphViz file using particle in Edge representation"""

    print "Writing GraphViz file to %s" % gvFilename
    with open(gvFilename, "w") as gvFile:
        # Now process the particles and add appropriate links to GraphViz file
        gvFile.write("digraph g {\n"
                     "\trankdir=LR;\n"
                     "\tranksep=0.4\n"
                     "\tnodesep=0.4\n")

        if not useRawNames:
            # Lots of dot2tex specific options
            libs = "\\usetikzlibrary{decorations.pathmorphing,fit,backgrounds,positioning}"
            styles = "\\tikzset{ \n" \
                     "\t\tstandard/.style={circle,minimum size=4bp,inner sep=0pt,fill,draw=black},\n" \
                     "\t\ttransparent/.style={circle},\n" \
                     "\t\tgluon/.style={gray,semitransparent,thin,decorate," \
                     "decoration={coil,amplitude=3bp,segment length=4bp}},\n" \
                     "\t\tphoton/.style={decorate,decoration={snake,post length=5bp}}\n" \
                     "\t}"
            hard_vertex = "V3"  # set me somewhere!
            highlight_box = '% Highlight the hard process\n' \
                            '\t\\begin{scope}[on background layer]\n' \
                            '\t\t\\node[fill=black!30,inner sep=10bp,fit=('\
                            + hard_vertex +')]{};\n' \
                            '\t\\end{scope}'

            gvFile.write('\t// Options just for dot2tex:\n')
            gvFile.write('\td2tdocpreamble="%s"\n' % libs)
            gvFile.write('\td2tfigpreamble="%s"\n' % styles)
            gvFile.write('\ttexmode="math"\n')
            gvFile.write('\td2tgraphstyle="very thick,scale=0.7,transform shape"\n')
            gvFile.write('\td2tfigpostamble="%s"\n' % highlight_box)

        for p in event.particles:

            if p.skip:
                continue

            p.display_attr.rawNames = useRawNames
            p.display_attr.setAttributesForEdge(
                interestingList=CONFIG.interesting)

            # Do particle line from vertex to vertex
            entry = '\t%s -> %s %s\n' % (
                p.edge_attr.outVertex.barcode,
                p.edge_attr.inVertex.barcode,
                p.display_attr.getEdgeString())

            gvFile.write(entry)
            if CONFIG.VERBOSE:
                print entry,

        # Print vertex display attributes, all the same for now
        for v in event.vertices:
            if v.skip:
                continue

            if useRawNames:
                color = "black"
                if v.isInitialState or v.isFinalState:
                    color = "transparent"
                entry = '    %s [label="%s",shape="point", size=0.1, color=%s]\n' \
                    % (v.barcode, v.barcode, color)
            else:
                style = "standard"
                if v.isInitialState or v.isFinalState:
                    style = "transparent"
                entry = '\t%s [label="", style="%s"]\n' % (v.barcode, style)

            gvFile.write(entry)
            if CONFIG.VERBOSE:
                print entry,

        # Set all initial vertices to be level in diagram
        rank = "  {rank=same;"
        initial = [p.edge_attr.outVertexBarcode for p in event.particles
                   if p.isInitialState]
        rank += ' '.join(initial)
        rank += "} // Put initial particles on same level\n"
        if CONFIG.VERBOSE: print rank,
        gvFile.write(rank)

        gvFile.write("}")
        gvFile.write("")