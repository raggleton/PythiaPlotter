# PythiaPlotter

This is a little script that uses GraphViz to plot Feynman-esque diagrams of Pythia 8 event listings. Very handy to figure out what is actually going on!

By default, the incoming protons are coloured green, and the final-state particles are in yellow boxes, to aid quick recognition.

## Requires:
- graphviz http://www.graphviz.org/Download..php

## Optional:
- Pythia 8 

## Instructions:

- Clone this repo:
	```
	git clone https://github.com/raggleton/PythiaPlotter.git # https

	```
	or 
	```
	git clone git@github.com:raggleton/PythiaPlotter.git # ssh

	```
- Copy the Pythia event listing into a text file, e.g. see `testLine.txt`. Note, you must only have the raw table data, not the column headings or the energy/momentum summary at the end
- Edit the `makeGraphFromPythia.py` script for correct input and output filenames
- Run the script to produce a GraphViz file:
	```
	./makeGraphFromPythia.py
	```
- Run `dot` over your GraphViz file to make the plot:
	```
	dot -Tpdf myEvent2.gv -o myEvent2.pdf
	```
This will output a PDF file of the event. Change filenames as necessary.

- Note, there's a bash script, `makeGraphFromPythia.sh`, that is old and out of date. Only kept for posterity.

## Future plans
- [ ] Combine with Latex to represent particle names properly
- [ ] Make into interactive diagram, so that if you mouse-over a particle, you can see what it decays into and where it's from easily (highlight, or make everything else transparent)
- [x] Simplify particle lines where you get repeats e.g. `195:g -> 278:g -> 323:g -> 394:g` to become `195:g -> 394:g`
- [x] Add option of highlighting user-specified particles in the graph (e.g. interested in production of certain particles)
	- [x] Improve by stripping any `()` from around the particle name to test if == one of interesting particles - allows exact matching (ATM does match to `*particleName*` which fails for say `b` quark)
- [x] Make a bit more user-friendly
- [x] Redo in python!