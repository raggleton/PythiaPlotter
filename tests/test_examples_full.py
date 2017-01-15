"""
These tests are designed to run the program in full using the included examples.
"""


import os
from pythiaplotter.PythiaPlotter import main


class RunOptions(object):
    """Class to store and inject options for a run of the program"""


    # TODO: design this better, very basic atm
    def __init__(self, input_filename, output_pdf, input_format):
        self.input_filename = input_filename
        self.output_pdf = output_pdf
        self.input_format = input_format

    def run_opts(self):
        result = main([self.input_filename, '-O', self.output_pdf, '--inputFormat', self.input_format])
        if result == 0:
            os.remove(self.output_pdf)
            os.remove(self.output_pdf.replace('.pdf', '.gv'))


def test_run_py8():
    r = RunOptions("example/example_pythia8.txt", 'test_py8.pdf', 'PYTHIA')
    r.run_opts()


def test_run_hepmc():
    r = RunOptions("example/example_hepmc.hepmc", 'test_hepmc.pdf', 'HEPMC')
    r.run_opts()


def test_run_cmssw():
    r = RunOptions("example/example_cmssw.txt", 'test_cmssw.pdf', 'CMSSW')
    r.run_opts()


def test_run_lhe():
    r = RunOptions("example/example_lhe.lhe", 'test_lhe.pdf', 'LHE')
    r.run_opts()
