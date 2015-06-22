# PythiaPlotter

![Travis Build Status](https://travis-ci.org/raggleton/PythiaPlotter.svg?branch=restructure_jan_2015)

## What Is It
Plots diagrams of particle decay trees in HEP Monte Carlo events. Very handy to figure out what is actually going on in your MC!

See examples in [`example`](example) folder.

## What can I give it to plot?

Currently supporting:

- Pythia 8 STDOUT (i.e. the big particle listing table) *(see [example/example_pythia8.txt](example/example_pythia8.txt))*
- HepMC files *(see [example/example_hepmc.hepmc](example/example_hepmc.hepmc))*
- LHE files *(see [example/example_lhe.lhe](example/example_lhe.lhe))*
- ParticleListDrawer STDOUT as output by CMSSW *(see [example/example_cmssw.txt](example/example_cmssw.txt))*

## What Do I Need:

- graphviz (get it from www.graphviz.org)
- Your favourite MC generator
- Some python packages: networkx/pydot2/pyparsing/dot2tex. To easily install these:
```
pip install -r requirements.txt
```

## How Do I Get It:

- Clone this repo:
	```
	git clone https://github.com/raggleton/PythiaPlotter.git # https

	# or

	git clone git@github.com:raggleton/PythiaPlotter.git # ssh
	```

## How Do I Use It:

Quick demo to see what it can do:
```
python PythiaPlotter.py --help
python PythiaPlotter.py example/example_pythia8.txt --openPDF
python PythiaPlotter.py example/example_hepmc.hepmc --openPDF
```

## What Else Should I Know:

- If you are feeling brave, use the latest, greatest version in the `restructure_jan_2015` branch, or for an example of the TikZ layout, look in the `hepMcReader` branch.

## What Improvements Are Being Working On:

See TODO.md

Wishlist:

- Parse: More parsers?
- Printer: JS?
