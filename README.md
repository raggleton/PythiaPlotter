# PythiaPlotter
---------------

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
- Edit the `makeGraphFromPythia.sh` script for correct input and output filenames
- Run the script to produce a GraphViz file:
	```
	./makeGraphFromPythia.sh
	```
- Run `dot` over your GraphViz file to make the plot:
	```
	dot -Tpdf myEvent.gv -o myEvent.pdf
	```
This will output a PDF file of the event. Change filenames as necessary.


## Future plans
----------------

[ ] Combine with Latex to represent particle names properly
[ ] Add option of highlighting user-specified particles in the graph (e.g. interested in production of certain particles)
[ ] Make a bit more user-friendly
[ ] Redo in python!