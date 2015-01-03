# PythiaPlotter

## > WHAT IS IT
This is a little script that plots diagrams of particle interactions in MC events using GraphViz (& optionally Latex). Very handy to figure out what is actually going on in your MC!

It currently accepts as input:
- screen output from PYTHIA8 (see [`qcdScatterSmall.txt`](qcdScatterSmall.txt) for example)
- **_In Development_** hepmc files

It also does fancy things like colour initial/final state particles in different colours, and can use Latex to make fancier looking diagrams.

For examples, see `qcdScatterSmall.pdf` and `qcdScatterSmall.gv`, which use the Pythia output in `qcdScatterSmall.txt`. This is a simulation of a pp -> g ubar scatter -> b bbar ubar, with subsequent hadronisation.

## > WHAT DO I NEED:
- GraphViz http://www.GraphViz.org/Download..php

**Optional:** (if you don't install these, you can only use `--outputMode DOT` option)

- dot2tex: `pip install dot2tex` https://github.com/kjellmf/dot2tex
- ~~dot2texi: check if included in your TeX distribution (use TeX Live utility or equivalent)~~
- TikZ: check if included in your TeX distribution (use TeX Live utility or equivalent)
- pydot: `pip install pydot` https://code.google.com/p/pydot/
- pyparsing: `pip install pyparsing` http://pyparsing.wikispaces.com/
- Pythia 8 http://home.thep.lu.se/~torbjorn/Pythia.html (for actually generating events)
- Or your favourite MC generator, so logn as it outputs in hepmc format

## > HOW DO I GET IT:

- Clone this repo:
	```
	git clone https://github.com/raggleton/PythiaPlotter.git # https

	```
	or 
	```
	git clone git@github.com:raggleton/PythiaPlotter.git # ssh

	```
	
## > HOW DO I USE IT:

- **If using PYTHIA8 screen output as input for plotter:** Copy the entire Pythia output into a text file, e.g. see `qcdScatterSmall.txt`. Note, you don't have to edit the Pythia output at all - the script will automatically find the hard and full event listings from the output.

- Have a look at possible options/flags:
	```
	python PythiaPlotterNew.py -h

	```
Outputs:

	```
	usage: PythiaPlotterNew.py [-h] [-i INPUT] [--inputType {HEPMC,PYTHIA}]
                           [--eventNumber EVENTNUMBER] [-oGV OUTPUTGV]
                           [-oPDF OUTPUTPDF] [--openPDF] [-p {NODE,EDGE}]
                           [--noPDF] [-oMode {LATEX,DOT}] [--straightEdges]
                           [--showVertexBarcode]
                           [--hardVertices [HARDVERTICES [HARDVERTICES ...]]]
                           [--noTimeArrows] [--scale SCALE] [-v]

    Convert PYTHIA8 or HepMC event listing into diagram using
    dot/GraphViz/dot2tex/pdflatex
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            input text file with Pythia 8 output (if unspecified,
                            defaults to qcdScatterSmall.txt)
      --inputType {HEPMC,PYTHIA}
                            input type, either HEPMC or PYTHIA (latter for the
                            *direct* output from Pythia8 on screen). If
                            unspecified, will try and make an educated guess, but
                            could fail!
      --eventNumber EVENTNUMBER
                            For HepMC file, select event number to plot
      -oGV OUTPUTGV, --outputGV OUTPUTGV
                            output GraphViz filename (if unspecified, defaults to
                            INPUT.gv)
      -oPDF OUTPUTPDF, --outputPDF OUTPUTPDF
                            output graph PDF filename (if unspecified, defaults to
                            INPUT.pdf)
      --openPDF             automatically open PDF once plotted
      -p {NODE,EDGE}, --particleMode {NODE,EDGE}
                            particle representation on PDF: NODE or EDGE
      --noPDF               don't convert to PDF
      -oMode {LATEX,DOT}, --outputMode {LATEX,DOT}
                            output method: LATEX, or DOT (no nice text/particle
                            edge formatting, but faster)
      --straightEdges       use straight edges instead of curvy
      --showVertexBarcode   show vertex barcodes, useful for figuring out which
                            are the hard interaction(s)
      --hardVertices [HARDVERTICES [HARDVERTICES ...]]
                            list of vertex barcode(s) that contain the hard
                            interaction, e.g. --hardVertices V2, V3
      --noTimeArrows        turn off the "Time" arrows
      --scale SCALE         factor to scale PDF by (Tex mode only atm)
      -v, --verbose         print debug statements to screen
	```

- To see what it can do, run the script to produce a GraphViz PDF from example PYTHIA8 output, using pdflatex (see `qcdScatterSmall.txt`):
	```
	python PythiaPlotterNew.py

	```
	The output PDF file is `qcdScatterSmall.pdf` unless the `-oPDF` option is used.

	Note, if you have a lot of particles, this can take a little while, so be patient. The program automatically highlights and changes node shapes for certain particles. These are defined in [CONFIG.py](config.py).
	

## > WHAT ELSE SHOULD I KNOW:

- Please run with `python PythiaPlotter.py` not `./PythiaPlotter.py`. For some reason, some things don't work properly using the latter **TO BE CONFIRMED**

- Note, there's a bash script, `DO_NOT_USE_makeGraphFromPythia.sh`, that is old and out of date. Only kept for posterity, and as a reminder of how painful bash can be.

- There's a not totally dissimilar program, HepMC Visual, that does something similar but requires ROOT, and you have to write your own script. So YMMV.

## > WHAT IMPROVEMENTS ARE BEING WORKING ON:

See [TODO](TODO.md)
