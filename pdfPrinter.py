"""Print GraphViz file to PDF

Can either do with raw strings particle names (fast but less pretty),
or TeX particle names (slower, but more pretty + configurations opts viz TikZ)
"""

import os.path
from subprocess import call
from subprocess import check_output
from sys import platform as _platform
import re
import argparse
import dot2tex as d2t

# PythiaPlotter files:
import config as CONFIG


def print_pdf(args, stemName, gvFilename, pdfFilename):
    """Print GraphViz file (gvFilename) to pdf (pdfFilename).
    stemName is for tex file. Should probably just use pdfFilename"""

    print "Producing PDF %s" % pdfFilename
    if args.outputMode == "DOT":
        # Just use dot to make a pdf quickly, no need for LaTeX
        run_dot(gvFilename, pdfFilename)
    elif args.outputMode == "LATEX":
        # Run pdflatex with dot2tex to make nice greek letters, etc. Slower.
        # run_latex(args, gvFilename, pdfFilename)
        run_dot2tex(args, gvFilename, pdfFilename)

    # Automatically open the PDF on the user's system if desired
    if args.openPDF and not args.noPDF:
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
    # dotargs = ["dot", "-Tps2", gvFilename, "-o", psFilename]
    dotargs = ["dot", "-Tpdf:quartz", gvFilename, "-o", pdfFilename]
    call(dotargs)
    # psargs = ["ps2pdf", psFilename, pdfFilename]
    # call(psargs)

    print ""
    print "To re-run:"
    print ' '.join(dotargs)#, "&&", ' '.join(psargs)
    print ""


def run_latex(args, gvFilename, pdfFilename):
    """Run latex with dot2tex"""
    # Use latex to make particle names nice.
    # Make a tex file for the job so can add user args, etc
    # Too difficult to use \def on command line
    d2tOpts = ''
    if args.straightEdges:
        d2tOpts = ",straightedges"

    # Pass relative path of gv & pdf file as TeX doesn't like absolute paths
    texTemplate = r"""\documentclass[tikz]{standalone}
\usepackage{dot2texi}
\usepackage{tikz}
\usepackage{xcolor}
\usetikzlibrary{shapes,arrows,snakes}

\begin{document}
\begin{dot2tex}[dot,mathmode,format=tikz,options={--graphstyle "very thick"}"""+d2tOpts+r"""]
\input{"""+os.path.relpath(gvFilename)+r"""}
\end{dot2tex}
\end{document}
"""
    texName = pdfFilename.replace(".pdf", ".tex")
    with open(texName, "w") as texFile:
        texFile.write(texTemplate)

    print "Producing tex file and running pdflatex (may take a while)"

    if CONFIG.VERBOSE: print texTemplate,

    # Optionally call pdflatex
    texargs = ["pdflatex", "--shell-escape", '-jobname',
               os.path.relpath(os.path.splitext(pdfFilename)[0]),
               texName]
    if args.noPDF:
        print ""
        print "Not converting to PDF"
        print "If you want a PDF, run without --noPDF"
        print "and if you only want the raw names (faster to produce),"
        print "then run with --rawNames"
        print ""
    else:
        call(texargs)

    print ""
    print "If you want to rerun the tex file for whatever reason, do:"
    print ' '.join(texargs)
    print ""
    print "Written PDF to", pdfFilename


def run_dot2tex(args, gvFilename, pdfFilename):
    """Run dot2tex module to convert graphviz to tikz in tex format"""

    # Need graph as string to pass to dot2tex module
    graph = ""
    with open(gvFilename, "r") as gvFile:
        graph += gvFile.read()

    # Use dot2tex to make tex file
    # First convert to xdot format?
    # xdot = check_output(["dot", "-Txdot", gvFilename])

    # edge_opts = "gluon/.style={gray,semitransparent,thin}"

    # TODO: print out this command. args as dict?
    kwargs = {'format': 'tikz',
              'tikzedgelabels': True,
              'straightedges': args.straightEdges
              # 'styleonly': True,  # True for EDGE, false for NODE, for time being TODO: needs fixing
              # 'edgeoptions': edge_opts,
              # 'progoptions': "-Gsize=6,12!"
    }

    texcode = d2t.dot2tex(graph,
                          **kwargs
                          # usepdflatex=True,  # use pdflatex for preprocessing
                          # autosize=True,
    )

    # Make some amendments to the tex code
    # Need to use standalone class to get right page size
    # TODO: use template?
    texcode = texcode.replace("{article}", "{standalone}")
    texcode = texcode.replace("\enlargethispage{100cm}", "")
    # Remove a silly background layer that dot2tex inserts that conflicts with
    # TikZ's ability to do [on background layer]
    p = re.compile(r'\\begin\{scope\}\n.*pgfsetstrokecolor.*?\\end\{scope\}',
                   re.DOTALL)  # keep the ? to make it non-greedy
    texcode = re.sub(p, "", texcode)

    # Figure out canvas size
    # p_node = re.compile(r'\\node \(V[0-9]*\) at \(([.0-9]*)bp,([.0-9]*)bp\)')
    # coords = p_node.findall(texcode)
    # x_max = 0
    # y_max = 0
    # x_min = 10000
    # y_min = 10000
    # for i in coords:
    #     # has to be a better way of doing this - lambda? unpacking?
    #     x, y = float(i[0]), float(i[1])
    #     if x > x_max:
    #         x_max = x
    #     elif x < x_min:
    #         x_min = x
    #     if y > y_max:
    #         y_max = y
    #     elif y < y_min:
    #         y_min = y
    # print "max:", x_max, y_max
    # print "min:", x_min, y_min

    texName = pdfFilename.replace(".pdf", ".tex")
    with open(texName, "w") as texFile:
        texFile.write(texcode)

    # Optionally call pdflatex
    texargs = ["pdflatex",
               '-interaction=nonstopmode',
               # '-halt-on-error', '-file-line-error',
               '-jobname',
               os.path.relpath(os.path.splitext(pdfFilename)[0]),
               texName]

    if args.noPDF:
        print ""
        print "Not converting to PDF"
        print "If you want a PDF, run without --noPDF"
        print "and if you only want the raw names (faster to produce),"
        print "then run with --rawNames"
        print ""
    else:
        call(texargs)

    print ""
    print "If you want to rerun the tex file for whatever reason, do:"
    print ' '.join(texargs)
    print ""
    print "Written PDF to", pdfFilename