""" These tests are designed to run the program in full using the included examples."""


from __future__ import absolute_import
from pythiaplotter.PythiaPlotter import main
import pytest


def test_run_py8():
    main(["example/example_pythia8.txt", '-O', 'test_py8.pdf', '--inputFormat', 'PYTHIA'])


def test_run_py8_convert():
    main(["example/example_pythia8.txt", '-O', 'test_py8_conv.pdf', '--inputFormat', 'PYTHIA', '-r', 'EDGE'])


def test_run_hepmc():
    main(["example/example_hepmc.hepmc", '-O', 'test_hepmc.pdf', '--inputFormat', 'HEPMC'])


def test_run_hepmc_convert():
    main(["example/example_hepmc.hepmc", '-O', 'test_hepmc_conv.pdf', '--inputFormat', 'HEPMC', '-r', 'NODE'])


def test_run_cmssw():
    main(["example/example_cmssw.txt", '-O', 'test_cmssw.pdf', '--inputFormat', 'CMSSW'])


def test_run_lhe():
    main(["example/example_lhe.lhe", '-O', 'test_lhe.pdf', '--inputFormat', 'LHE'])


def test_run_lhe_ps():
    main(["example/example_lhe.lhe", '-O', 'test_lhe_ps.pdf', '--inputFormat', 'LHE',
          '--outputFormat', 'ps'])


def test_run_lhe_jpeg():
    main(["example/example_lhe.lhe", '-O', 'test_lhe.jpg', '--inputFormat', 'LHE'])


def test_run_heppy():
    pyroot = pytest.importorskip("ROOT")
    main(["example/example_heppy.root", '-O', "test_heppy.pdf", '--inputFormat', "HEPPY"])
