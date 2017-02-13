"""These tests are meant to run using the included examples either in full, or just parsing args."""


from __future__ import absolute_import
import pytest
from pythiaplotter.PythiaPlotter import main
from pythiaplotter.cli import get_args


FUNC = get_args


@pytest.mark.xfail
def test_run_no_input(main_func=FUNC):
    main_func(['--inputFormat', 'PYTHIA'])


def test_run_py8_minimal(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '--inputFormat', 'PYTHIA', '--stats'])


def test_run_py8_redundants(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '-O', 'test_py8.pdf', '--inputFormat', 'PYTHIA', '--redundants'])


def test_run_py8_ofmt(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '--outputFormat', 'pdf', '--inputFormat', 'PYTHIA', '--redundants'])


def test_run_py8_convert(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '-O', 'test_py8_conv.pdf', '--inputFormat', 'PYTHIA', '-r', 'EDGE'])


def test_run_py8_sfdp(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '-O', 'test_py8_conv.pdf', '--inputFormat', 'PYTHIA', '--layout', 'sfdp'])


def test_run_py8_web(main_func=FUNC):
    main_func(["example/example_pythia8.txt", '-O', 'test_py8.html', '--inputFormat', 'PYTHIA', '--printer', 'WEB'])


def test_run_dump_config(main_func=FUNC):
    main_func(["--dumpConfig"])


def test_run_hepmc(main_func=FUNC):
    main_func(["example/example_hepmc.hepmc", '-O', 'test_hepmc.pdf', '--inputFormat', 'HEPMC'])


def test_run_hepmc_guess_input(main_func=FUNC):
    main_func(["example/example_hepmc.hepmc", '-O', 'test_hepmc.pdf'])


def test_run_hepmc_redundants(main_func=FUNC):
    main_func(["example/example_hepmc.hepmc", '-O', 'test_hepmc.pdf', '--inputFormat', 'HEPMC', '--redundants'])


def test_run_hepmc_convert(main_func=FUNC):
    main_func(["example/example_hepmc.hepmc", '-O', 'test_hepmc_conv.pdf', '--inputFormat', 'HEPMC', '-r', 'NODE'])


def test_run_hepmc_web(main_func=FUNC):
    main_func(["example/example_hepmc.hepmc", '-O', 'test_hepmc.html', '--inputFormat', 'HEPMC', '--printer', 'WEB'])


def test_run_cmssw(main_func=FUNC):
    main_func(["example/example_cmssw.txt", '-O', 'test_cmssw.pdf', '--inputFormat', 'CMSSW'])


def test_run_lhe(main_func=FUNC):
    main_func(["example/example_lhe.lhe", '-O', 'test_lhe.pdf', '--inputFormat', 'LHE'])


def test_run_lhe_ps(main_func=FUNC):
    main_func(["example/example_lhe.lhe", '-O', 'test_lhe_ps.pdf', '--inputFormat', 'LHE', '--outputFormat', 'ps'])


def test_run_heppy(main_func=FUNC):
    pytest.importorskip("ROOT")
    main_func(["example/example_heppy.root", '-O', "test_heppy.pdf", '--inputFormat', "HEPPY"])
