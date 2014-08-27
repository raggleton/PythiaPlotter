# Future plans/TODO

(not in any particular order)

- [ ] Let pdflatex run normally instead of trying to hide output, otherwise can look like it hangs for no reason
- [x] **_BIG_ - and mostly done (in master branch)** Combine with Latex to represent particle names properly
    - [ ] Add user option to pass options to dot2texi
    - [x] Redo ugly rewriting gv into tex file by linking or something
    - [x] Do test to see if the necessary programs exist
- [ ] **_BIG_ - see hepmcParser branch** Use HepMC to actually parse a HepMC file, not just copy and paste the output...
    - [ ] Draw like normal Feynman diagram, not the current inverse look. Or give user the choice
    - [ ] Use pyparsing to ease parsing of file/event info?
    - [ ] Just wrap HepMC instead of implementing subset/whole of it?
    - [ ] Unify a_variable and aVariable (hangover from HepMC?)
    - [ ] Throw some exceptions (e.g. HeavyIon lines, wrong units)
    - [ ] Test, test, test!!!
    - [x] Auto determine if output of Pythia, or HepMC (and act accordingly)
    - [x] Allow user to select which event to look at in HepMC file
- [ ] **_BIG_ - slow start, see siteDev branch** Make into interactive diagram, so that if you mouse-over a particle, you can see what it decays into and where it's from easily (highlight, or make everything else transparent)
- [ ] **_BIG_ - not even looked at yet** Parse LHE files
- [ ] Improve parsing of input file eg if only full event, or other listings

## DONE (well, mostly...)
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

### Current work 

_**hepmcParser**_:

- [ ] go from `--rawNames` to `tex` and `dot` modes (or something like that?)
- [ ] Fix NodeToEdge comversion
    - [ ] Do properly **ON HOLD - V.DIFFICULT**
- [ ] user options (curly splines, etc)?
- [ ] Fix DisplayAttributes/pdfPrinter/dot2tex implementation
    - [ ] does `arrowsize` even do anything?
    - [ ] More feynman-like:
        - [ ] arrow in middle: `--->---`
        - [ ] gluons are spirals
        - [x] wavy lines for bosons
        - [x] higgs bosons are dashed: `- - - - -`
    - [ ] TikZ styles for Edges
    - [ ] Centralise styles so easily accessible in DisplayAttributes, edgeWriter, pdfPrinter
    - [ ] (Printer class instead of jsut fns)
    - [ ] Fix colours (use camelCase)
    - [ ] Legend on plot?
    - [ ] Template for dot2tex *hard - doesn't seem to accept it from py module, doesn't insert things properly*
    - Where should I put all my options for dot2tex? When calling it from module? Or in gv file, so easier to process later? ATM scattered about the place...
    - [x] use `dot2tex` module, don't write own tex file
    - [x] `penwidth`, `transparent` not obeyed (for latter, remove fill in [], so just \node...[circle])
    - [x] do some preprocessing to do spacing better?
    - [x] nodes are huge in tex mode
    - [x] increase horizontal spacing
    - [x] Default curved edges for all modes?
    - [x] mathmode not being respected for edges, but is for nodes? -> __Use `texlbl` and `label=" "`, SPACE IN `label` IS VITAL__
    - [x] colours go screwy (edge only)
    - [x] points are too big
    - [x] labels not colored *may not colour them for clarity*
- [ ] Event post-processing common for both parsers - hide away? do separately?

*Less pressing issues:*

- [ ] Rename all functions/attributes from `camelCase` to `underscore_rulez`
- [ ] do docstrings properly: https://docs.python.org/2/tutorial/controlflow.html#documentation-strings
- [ ] add proton beam info to GenEvent?
- [ ] `__repr__` functions better
- [ ] Add test to parse() methods to check if suitable format or not
- [ ] Add more tests for all classes/methods

*DONE:*

- [x] be able select interesting particles via PDGID as well as name
- [x] make PDF searchable by doing `dot -Tps2` then `ps2pdf` on PostScript file
- [x] Test removeRedundants & write for Edge case
- [x] Output for gv and pdf/tex should respect folder, not just dump it wherever python is called from
- [x] oddity with incoming proton self edge
- [x] DisplayAttributes use dict to generate strings
- [x] Rename `xxxAttributes` to `xxx_attr` for brevity
- [x] barcode to string, use V for vertex **Done for GenVertex only**
- [x] Set initial/final state for hepmcParser
- [x] add suffix to PDF filename for edge or node
- [x] rename "colour" to "color" in DisplayAttributes
- [x] Restructure PythiaPlotter (see PythiaPlotterNew.py)
- [x] Subclass GenParticle for Edge/Node specifics. Or have attribute classes
- [x] redo sameInitialOnes in nodeParser.py
- [x] Create GenEvent object in pythiaParser, fill it with particles, return it.
- [x] Add more tests for conversions
- [x] Add conversions from NodeAttributes to EdgeAttributes **test**
- [x] How to run all tests in pycharm? **easy: http://www.jetbrains.com/pycharm/webhelp/creating-run-debug-configuration-for-tests.html**
- [x] Add invertices to final states particles so that we can draw them
- [x] Redo add NodeMothers to correct particles[m]. Use dictionary in GenEvent? Or Getter?
- [x] Need some SetDisplayAttributes method to centralise it.

Photons:
\usetikzlibrary{shapes,arrows,snakes}
return '[label=" ", texlbl="$%s$", color="%s", fontcolor="%s", arrowsize=0.8, width=2, style="snake=snake" ]\n'\
