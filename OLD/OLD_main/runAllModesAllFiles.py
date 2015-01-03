import os.path
import subprocess
from subprocess import call
from sys import platform as _platform


modes = ["EDGE", "NODE"]
files = ["test_1to2.txt", "test_1to2.hepmc",
         "test_2to1.txt", "test_2to1.hepmc",
         "test_3to1to2.txt", "test_3to1to2.hepmc", ]
names = ["--rawName"]#, ""]

openPDF = "--openPDF"

for m, f, n in [(m, f,n) for m in modes for f in files for n in names]:
    print m, f, n
    call(["python", "PythiaPlotterNew.py", "-i", "test/testSamples/"+f, "-m", m, openPDF, n])