#!/bin/bash
dot -Teps myEvent.gv -o myEvent.eps
latex convert.tex 
dvips -o plot.ps convert.dvi 
ps2pdf plot.ps plot.pdf
