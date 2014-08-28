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
                     "\t\tpoint node/.style={circle,minimum size=4bp,inner sep=0pt,fill,draw=black},\n" \
                     "\t\tnamed node/.style={circle,draw=black},\n" \
                     "\t\ttransparent node/.style={circle},\n" \
                     "\t\tgluon/.style={gray,semitransparent,thin,decorate," \
                     "decoration={coil,amplitude=3bp,segment length=4bp}},\n" \
                     "\t\tphoton/.style={decorate,decoration={snake,post length=5bp}}\n" \
                     "\t}"
            # gluon must be thin - if you change the scale of the picture,
            # also fiddle with gluon line width and amplitude/segment length to
            # avoid exceeding memory
            gvFile.write('\t// Options just for dot2tex:\n')
            gvFile.write('\td2tdocpreamble="%s"\n' % libs)
            gvFile.write('\td2tfigpreamble="%s"\n' % styles)
            gvFile.write('\ttexmode="math"\n')
            gvFile.write('\td2tgraphstyle="very thick,scale=0.7,transform shape"\n')

            # If desired, draw box for hard interaction - user must specify
            # the vertices via command line option
            if CONFIG.args.hardVertices:
                hard_vertices = ') ('.join(CONFIG.args.hardVertices)
                # Note, the 40bp spacing is required to actually encompass the
                # nodes - may need even more if you find it doesn't go all the
                # way. IT should do this automatically, but think there's
                # a possible scaling issue
                highlight_box = '% Highlight the hard process\n' \
                                '\t\\begin{scope}[on background layer]\n' \
                                '\t\t\\node[fill=blue!30,inner sep=40bp,' \
                                'label=above:\Large Hard interaction,' \
                                'fit=(' + hard_vertices + ')]{};\n' \
                                '\t\\end{scope}'
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
                style = "point node"
                label = ""
                if CONFIG.args.showVertexBarcode:
                    style = "named node"
                    label = v.barcode

                if v.isInitialState or v.isFinalState:
                    style = "transparent node"

                entry = '\t%s [label="%s", style="%s"]\n' % (v.barcode,
                                                             label,
                                                             style)

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