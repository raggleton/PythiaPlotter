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
        # Just use dot to make a pdf quickly, no need for LaTeX
        run_dot(gvFilename, pdfFilename)
    else:
        # Run pdflatex with dot2tex to make nice greek letters, etc. Slower.
        run_latex(args, gvFilename, pdfFilename)

    # Automatically open the PDF on the user's system if desired
    if args.openPDF:
        open_pdf(pdfFilename)


def open_pdf(pdfFilename):
    """Open a PDF file using system's default PDF viewer."""
    if _platform.startswith("linux"):
        # linux
        call(["xdg-open", pdfFilename])
    elif _platform == "darwin":
        # OS X
        call(["open", pdfFilename])
    elif _platform == "win32":
        # Windows
        call(["start", pdfFilename])


def run_dot(gvFilename, pdfFilename):
    """Run GraphViz file through dot to produce a PDF."""
    # Do 2 stages: make a PostScript file, then convert to PDF.
    # This makes the PDF searchable.
    psFilename = pdfFilename.replace(".pdf", ".ps")
    dotargs = ["dot", "-Tps2", gvFilename, "-o", psFilename]
    call(dotargs)
    psargs = ["ps2pdf", psFilename, pdfFilename]
    call(psargs)

    print ""
    print "To re-run:"
    print ' '.join(dotargs)
    print ' '.join(psargs)
    print ""


def run_latex(args, gvFilename, pdfFilename):
    """Run latex with dot2tex"""
    # Use latex to make particle names nice.
    # Make a tex file for the job so can add user args, etc
    # Too difficult to use \def on command line
    d2tOpts = ""
    if args.StraightEdges:
        d2tOpts = ",straightedges"

    # Pass relative path of gv & pdf file as TeX doesn't like absolute paths
    texTemplate = r"""\documentclass[tikz]{standalone}
\usepackage{dot2texi}
\usepackage{tikz}
\usepackage{xcolor}
\usetikzlibrary{shapes,arrows,snakes}
\usetikzlibrary{decorations.pathmorphing}

\begin{document}
\begin{dot2tex}[dot,mathmode,format=tikz"""+d2tOpts+r"""]
\input{"""+os.path.relpath(gvFilename)+r"""}
\end{dot2tex}
\end{document}
"""
    texName = pdfFilename.replace(".pdf", ".tex")
    with open(texName, "w") as texFile:
        texFile.write(texTemplate)

    print "Producing tex file and running pdflatex (may take a while)"

    if CONFIG.VERBOSE: print texTemplate,

    texargs = ["pdflatex", "--shell-escape", '-jobname',
               os.path.relpath(os.path.splitext(pdfFilename)[0]),
               texName]
    call(texargs)

    print ""
    print "If you want to rerun the tex file for whatever reason, do:"
    print ' '.join(texargs)
    print ""
    print "Written PDF to", pdfFilename