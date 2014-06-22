# PythiaPlotter

This is a little script that uses GraphViz to plot Feynman-esque diagrams of Pythia 8 event listings. Very handy to figure out what is actually going on!

By default, the incoming protons are green circles, and the final-state particles are in yellow boxes, to aid quick recognition. The user can also highlist specific particle types in red (e.g. all muons, b quarks).

For examples, see `qcdScatterSmall.pdf` and `qcdScatterSmall.gv`, which use the Pythia output in `qcdScatterSmall.txt`

## Requires:
- graphviz http://www.graphviz.org/Download..php

## Optional:
- Pythia 8 http://home.thep.lu.se/~torbjorn/Pythia.html

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
	                        [-nD] [--openPDF] [--convertTex] [-v]

	Convert Pythia 8 event listing into graph using dot in Graphviz

	optional arguments:
	  -h, --help            show this help message and exit
	  -i INPUT, --input INPUT
	                        input text file with Pythia 8 output (if unspecified,
	                        defaults to qcdScatterSmall.txt)
	  -oGV OUTPUTGV, --outputGV OUTPUTGV
	                        output graphviz filename (if unspecified, defaults to
	                        INPUT.gz)
	  -oPDF OUTPUTPDF, --outputPDF OUTPUTPDF
	                        output graph PDF filename (if unspecified, defaults to
	                        INPUT.pdf)
	  -nD, --noDot          don't get dot to plot the resultant Graphviz file
	  --openPDF             automatically open PDF once plotted
	  --convertTex          convert to tex code using psfrag to represent particle
	                        names properly
	  -v, --verbose         print debug statements to screen
	```

- Run the script to produce a GraphViz file from example PYTHIA8 output (in `qcdScatterSmall.txt`):
	```
	python PythiaPlotter.py

	```
	The output PDF file is `qcdScatterSmall.pdf`.
	Note that by default, this will also run `dot` over the GraphViz file to produce a PDF plot. If you don't want it to, use `-nD, --noDot` flag.

## Notes:

- If you want all the particle names in the resultant PDF to look nice, use the `--convertTex` flag. Note that this is still experimental. In particular, running latex gives errors. Keep pressing `ENTER` though and it will still produce a nice PDF. For example, see `qcdScatterSmallConvert.pdf`, produced by running `python PythiaPlotter.py --convertTex`.

- If you used the `-nD, --notDot` flag, to run `dot` over your GraphViz file to make the plot:
	```
	dot -Tpdf qcdScatterSmall.gv -o qcdScatterSmall.pdf
	
	```
This will output a PDF file of the event.

- Note, there's a bash script, `DO_NOT_USE_makeGraphFromPythia.sh`, that is old and out of date. Only kept for posterity, and as a reminder of how painful bash can be.

## Future plans
- [ ] Any way to optimise the diagram? Sometimes lines go in weird paths
- [ ] Make into interactive diagram, so that if you mouse-over a particle, you can see what it decays into and where it's from easily (highlight, or make everything else transparent)
- [ ] Add check to see if PYTHIA output or not
- [ ] Combine with Latex to represent particle names properly **FIRST ATTEMPT DONE - STILL WORK IN PROGRESS**
- [x] Option to auto-open resultant PDF (make default?)
- [x] Command-line option for input txt filename (and output?)
- [x] Parse full Pythia output
- [x] Simplify particle lines where you get repeats e.g. `195:g -> 278:g -> 323:g -> 394:g` to become `195:g -> 394:g`
	- [ ] Fix - doesn't always work properly :confused:
- [x] Add option of highlighting user-specified particles in the graph (e.g. interested in production of certain particles)
	- [x] Improve by stripping any `()` from around the particle name to test if == one of interesting particles - allows exact matching (ATM does match to `*particleName*` which fails for say `b` quark)
- [x] Make a bit more user-friendly
- [x] Redo in python!