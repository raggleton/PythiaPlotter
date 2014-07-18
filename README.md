# PythiaPlotter

This is a little script that uses GraphViz to plot Feynman-esque diagrams of Pythia 8 event listings. Very handy to figure out what is actually going on!

By default, the incoming protons are green circles, and the final-state particles are in yellow boxes, to aid quick recognition. The user can also highlist specific particle types in certain colours (e.g. all muons in blue, all b quarks in red).

For examples, see `qcdScatterSmall.pdf` and `qcdScatterSmall.gv`, which use the Pythia output in `qcdScatterSmall.txt`. This is a simulation of a pp -> g ubar scatter -> b bbar ubar, with subsequent hadronisation.

## Requires:
- GraphViz http://www.GraphViz.org/Download..php

**Optional:** (if you don't install these, you can only use `--rawNames` option)

- dot2tex: `pip install dot2tex` https://github.com/kjellmf/dot2tex
- dot2texi: check if included in your TeX distribution (use TeX Live utility or equivalent)
- TikZ: check if included in your TeX distribution (use TeX Live utility or equivalent)
- pydot: `pip install pydot` https://code.google.com/p/pydot/
- pyparsing: `pip install pyparsing` http://pyparsing.wikispaces.com/
- Pythia 8 http://home.thep.lu.se/~torbjorn/Pythia.html (for actually generating events)

## Instructions:

- Clone this repo:
	```
	git clone https://github.com/raggleton/PythiaPlotter.git # https

	```
	or 
	```
	git clone git@github.com:raggleton/PythiaPlotter.git # ssh

	```
- Copy the entire Pythia output into a text file, e.g. see `qcdScatterSmall.txt`. Note, you don't have to edit the Pythia output at all - the script will automatically find the hard and full event listings from the output.
- Have a look at possible options/flags:
	```
	python PythiaPlotter.py -h

	```
Outputs:

	```
	usage: PythiaPlotter.py [-h] [-i INPUT] [-oGV OUTPUTGV] [-oPDF OUTPUTPDF]
                        [--openPDF] [--noPDF] [--rawNames] [--noStraightEdges]
                        [-v]

	Convert Pythia 8 event listing into graph using dot/GraphViz/dot2tex/pdflatex

	optional arguments:
	  -h, --help            show this help message and exit
	  -i INPUT, --input INPUT
	                        input text file with Pythia 8 output (if unspecified,
	                        defaults to qcdScatterSmall.txt)
	  -oGV OUTPUTGV, --outputGV OUTPUTGV
	                        output GraphViz filename (if unspecified, defaults to
	                        INPUT.gz)
	  -oPDF OUTPUTPDF, --outputPDF OUTPUTPDF
	                        output graph PDF filename (if unspecified, defaults to
	                        INPUT.pdf)
	  --openPDF             automatically open PDF once plotted
	  --noPDF               don't convert to PDF
	  --rawNames            don't convert particle names to tex, use raw string
	                        names - faster but less pretty
	  --noStraightEdges     don't use straight edges, curvy instead
	  -v, --verbose         print debug statements to screen
	```

- Run the script to produce a GraphViz PDF from example PYTHIA8 output, using pdflatex (see `qcdScatterSmall.txt`):
	```
	python PythiaPlotter.py

	```
	The output PDF file is `qcdScatterSmall.pdf` unless the `-oPDF` option is used.

	Note, if you have a lot of particles, this can take a little while, so be patient. The program automatically highlights and changes node shapes for certain particles:
	- Incoming protons are in green circles
	- Final state particles are in yellow boxes
	- Any "interesting" particles are highlighted in a colour of user's choice, by default b/bbar quarks are in red, muons in cyan.

	Note that by default, this will also create GraphViz and tex files. The latter uses the GraphViz file to produce a PDF with nice particle names. If you don't want nice names, or don't want to install all the extra stuff listed under "Optional" then use `--rawNames` flag

## Notes:

- Please run with `python PythiaPlotter.py` not `./PythiaPlotter.py`. For some reason, some things don't work properly using the latter **TO BE CONFIRMED**

- Note, there's a bash script, `DO_NOT_USE_makeGraphFromPythia.sh`, that is old and out of date. Only kept for posterity, and as a reminder of how painful bash can be.

- There's a not totally dissimilar program, HepMC Visual, that does something similar but requires ROOT, and you have to write your own script. So YMMV.

## Future plans/TODO
- [ ] Let pdflatex run normally instead of tryign to hide output, otherwise can look like it hangs for no reason
- [x] **_BIG_** Combine with Latex to represent particle names properly
	- [x] Redo ugly rewriting gv into tex file by linking or something
	- [ ] Add user option to pass options to dot2texi
	- [x] Do test to see if the necessary programs exist
- [ ] Use pyparsing to ease parsing of file/event info?
- [ ] Improve parsing of input file eg if only full event, or other listings
- [ ] **_BIG_** Use HepMC to actually parse a HepMC file, not just copy and paste the output...
	- [ ] Allow user to select which event to look at in HepMC file
- [ ] **_BIG_** Make into interactive diagram, so that if you mouse-over a particle, you can see what it decays into and where it's from easily (highlight, or make everything else transparent)

### DONE (well, mostly...)
- [x] Any way to optimise the diagram? Sometimes lines go in weird paths *solved using `straightedges` option in dot*
- [x] Option to auto-open resultant PDF (make default?)
- [x] Command-line option for input txt filename (and output?)
- [x] Parse full Pythia output
- [x] Simplify particle lines where you get repeats e.g. `195:g -> 278:g -> 323:g -> 394:g` to become `195:g -> 394:g`
	- [ ] Fix - doesn't always work properly :confused:
- [x] Add option of highlighting user-specified particles in the graph (e.g. interested in production of certain particles)
	- [x] Improve by stripping any `()` from around the particle name to test if == one of interesting particles - allows exact matching (ATM does match to `*particleName*` which fails for say `b` quark)
- [x] Make a bit more user-friendly
- [x] Redo in python!
