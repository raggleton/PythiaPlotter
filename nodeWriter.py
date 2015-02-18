"""
Prints relationships to GraphViz file when representing particles as nodes
(for edges see edgeWriter.py)
"""

import os.path
import eventClasses
import config as CONFIG


def printNodeToGraphViz(event, gvFilename, useRawNames=False):
    """Prints GenEvent to GraphViz file using particle in Node representation"""

    print "Writing GraphViz file to %s" % gvFilename
    with open(gvFilename, "w") as gvFile:
        # Now process the particles and add appropriate links to GraphViz file
        # Start from the end and work backwards to pick up all connections
        # (doesn't work if you start at beginning and follow daughters)
        gvFile.write("digraph g {\n"
             "\trankdir=RL;\n"
             "\tranksep=0.4\n"
             "\tnodesep=0.4\n")

        if not useRawNames:
            # Lots of dot2tex specific options
            docpreamble = "\\usetikzlibrary{decorations.pathmorphing,fit," \
                          "backgrounds,positioning,calc,decorations.markings}"
            figpreamble = "\\tikzset{ \n" \
                     "\tevery node/.style={circle,draw=black}\n" \
                     "\t}" \

            # Add in time arrows if user wants them
            graphstyle = "very thick,scale=" + str(CONFIG.args.scale) + \
                         ",transform shape," \
                         "execute at end picture={\n"
            if not CONFIG.args.noTimeArrows:
                time_arrow_top = \
                    r"\draw [->,line width=4bp,arrows={-latex[scale=3]}] ($(current bounding box.north)!0.07!(current bounding box.west)$) -- ($(current bounding box.north)!0.07!(current bounding box.east)$) node [midway,above,label=\Huge \textsc{Time}] {};"
                time_arrow_bottom = \
                    r"\draw [->,line width=4bp,arrows={-latex[scale=3]}] ($(current bounding box.south)!0.07!(current bounding box.west)$) -- ($(current bounding box.south)!0.07!(current bounding box.east)$) node [midway,above,label=\Huge \textsc{Time}] {};"
                graphstyle += "\t% Time arrows\n\t" + time_arrow_top + "\n" \
                              + "\t" + time_arrow_bottom + "\n"
            graphstyle += "\t}"
            # "\\node (legend-align) at ($(current bounding box.north west)!0.07!(current bounding box.south east)$) [align=left, anchor=north west,fill=black!20,label=above:\Huge \\textsc{Legend}] {AYE A TEST \\ line2};

            gvFile.write('\t// Options just for dot2tex:\n')
            gvFile.write('\td2tdocpreamble="%s"\n' % docpreamble)
            gvFile.write('\td2tfigpreamble="%s"\n' % figpreamble)
            gvFile.write('\ttexmode="math"\n')
            gvFile.write('\td2tgraphstyle="%s"\n' % graphstyle)

            # If desired, draw box for hard interaction - user must specify
            # the vertices via command line option
            if CONFIG.args.hardVertices:
                hard_vertices = ') ('.join(CONFIG.args.hardVertices)
                # Note, the 40bp spacing is required to actually encompass the
                # nodes - may need even more if you find it doesn't go all the
                # way. IT should do this automatically, but think there's
                # a possible scaling issue
                highlight_box = '\t'r'% Various regions to highlight''\n' \
                                '\t'r'\begin{scope}[on background layer]''\n' \
                                '\t\t'r'% Highlight hard process node(s)''\n' \
                                '\t\t'r'\node[scale=' \
                                + str(1./CONFIG.args.scale) + \
                                r',fill=blue!30,inner sep=20bp,' \
                                r'label=above:' \
                                r'\Large \textsc{Hard Interaction},' \
                                'fit=(' + hard_vertices + ')]{};\n' \
                                '\t'r'\end{scope}'
                gvFile.write('\td2tfigpostamble="%s"\n' % highlight_box)

        for p in reversed(event.particles):

            if p.skip or p.isRedundant or p.name == "system":
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

        # Add in node for sample, LS, evt number
        base_name = os.path.basename(gvFilename)
        sample = "_".join(base_name.split("_")[:2])
        LS = base_name.split("_")[-2]
        evt = base_name.split("_")[-1].replace(".gv", "")
        info_label = "%s,  LS: %s,  EVT: %s" % (sample, LS, evt)
        info_node = '-1 [label="%s", shape="box", style="filled", fillcolor="Yellow"]\n' % info_label
        gvFile.write(info_node)

        # Set all initial particles to be level in diagram
        rank = "  {rank=same; -1 "
        rank += ' '.join([str(p.barcode) for p in event.particles
                          if p.isInitialState and p.pdgid != 90])
        rank += "} // Put initial particles on same level\n"
        if CONFIG.VERBOSE: print rank,
        gvFile.write(rank)

        gvFile.write("}")
        gvFile.write("")