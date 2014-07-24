# Future plans/TODO

(not in any particular order)

- [ ] Let pdflatex run normally instead of trying to hide output, otherwise can look like it hangs for no reason
- [x] **_BIG_** Combine with Latex to represent particle names properly
    - [x] Redo ugly rewriting gv into tex file by linking or something
    - [ ] Add user option to pass options to dot2texi
    - [x] Do test to see if the necessary programs exist
- [ ] **_BIG_** Use HepMC to actually parse a HepMC file, not just copy and paste the output...
    - [ ] Draw like normal Feynman diagram, not the current inverse look. Or give user the choice
    - [ ] Use pyparsing to ease parsing of file/event info?
    - [ ] Allow user to select which event to look at in HepMC file
    - [ ] Auto determine if output of Pythia, or HepMC (and act accordingly)
    - [ ] Just wrap HepMC instead of implementing subset/whole of it?
    - [ ] Unify a_variable and aVariable (hangover from HepMC?)
    - [ ] Test, test, test!!!
        1. Test after parsing each line implemented, before worrying about all the connections
        2. Test the connections
        3. Test the writing to GraphViz format
- [ ] **_BIG_** Make into interactive diagram, so that if you mouse-over a particle, you can see what it decays into and where it's from easily (highlight, or make everything else transparent)
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