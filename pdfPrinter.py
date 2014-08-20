"""Print GraphViz file to PDF

Can either do with raw strings particle names (fast but less pretty),
or TeX particle names (slower, but more pretty + configurations opts viz TikZ)
"""

import os.path
from subprocess import call
from sys import platform as _platform
import argparse

# PythiaPlotter files:
import config as CONFIG


def print_pdf(args, stemName, gvFilename, pdfFilename):
    """Print GraphViz file (gvFilename) to pdf (pdfFilename).
    stemName is for tex file. Should probably just use pdfFilename"""

    print "Producing PDF %s" % pdfFilename
    if args.rawNames:
        # Just use dot to make a pdf quickly
        # Do 2 stages: make a PostScript file, then convert to PDF.
        # This makes the PDF searchable.
        psFilename = pdfFilename.replace(".pdf", ".ps")
        texargs = ["dot", "-Tps2", gvFilename, "-o", psFilename]
        call(texargs)
        psargs = ["ps2pdf", psFilename, pdfFilename]
        call(psargs)

        print ""
        print "To re-run:"
        print ' '.join(texargs)
        print ' '.join(psargs)
        print ""

    else:
        # Use latex to make particle names nice.
        # Make a tex file for the job so can add user args, etc
        # Too difficult to use \def on command line
        if not args.noStraightEdges:
            dttOpts = ",straightedges"
        else:
            dttOpts = ""

        texTemplate = r"""\documentclass{standalone}
\usepackage{dot2texi}
\usepackage{tikz}
\usepackage{xcolor}
\usetikzlibrary{shapes,arrows,snakes}
\begin{document}
\begin{dot2tex}[dot,mathmode"""+dttOpts+r"""]
\input{"""+gvFilename+r"""}
\end{dot2tex}
\end{document}
"""
        with open(stemName+".tex", "w") as texFile:
            texFile.write(texTemplate)

        print "Producing tex file and running pdflatex (may take a while)"

        if CONFIG.VERBOSE: print texTemplate,

        texargs = ["pdflatex", "--shell-escape", '-jobname',
                   os.path.splitext(pdfFilename)[0], stemName+".tex"]

        call(texargs)

    print ""
    print "If you want to rerun the tex file for whatever reason, do:"
    print ' '.join(texargs)
    print ""
    print "Written PDF to", pdfFilename

    ################################################
    # Automatically open the PDF on the user's system if desired
    ################################################
    if args.openPDF:
        if _platform.startswith("linux"):
            # linux
            call(["xdg-open", pdfFilename])
        elif _platform == "darwin":
            # OS X
            call(["open", pdfFilename])
        elif _platform == "win32":
            # Windows
            call(["start", pdfFilename])