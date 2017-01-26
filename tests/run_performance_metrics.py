"""Profiles various functions, etc to measure time taken, etc """


from __future__ import absolute_import, division, print_function
from timeit import repeat
from collections import OrderedDict
import os
import json


n_iter = 100
n_repeat = 5
do_comparison_store = True
store = "tests/.benchmark_cache"

previous_results = None

if do_comparison_store and os.path.isfile(store):
    with open(store) as f:
        previous_results = json.load(f)
        print("Loaded previous run results from", store)


GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'


def print_result(time, label, label_width=15, comparison=None):
    print_str = "{:.<%d} {:.3e} seconds" % label_width
    print_str = print_str.format(label, time)
    if comparison and label in comparison:
        prev_time = float(comparison[label])
        diff = time - prev_time
        if diff > 0:
            print_str += RED
        else:
            print_str += GREEN
        print_str += " ({:+.3e})".format(diff)
        print_str += ENDC
        frac_diff = abs(diff) / time
        if frac_diff > 0.1:
            print_str += " !!! {}% diff".format(int(round(100 * frac_diff)))
    print(print_str)


std_import = "gc.enable();import logging;" \
             "from pythiaplotter.utils.logging_config import root;" \
             "root.setLevel(logging.ERROR);" \
             "from pythiaplotter.utils.common import cleanup_filepath as cf;"

test_settings = OrderedDict()

# NODE based parsers
test_settings['py8 parser'] = dict(
    stmt='Pythia8Parser(cf("example/example_pythia8.txt"), 0).parse()',
    setup=std_import+"from pythiaplotter.parsers import Pythia8Parser",
    repeat=n_repeat,
    number=n_iter
)

test_settings['lhe parser'] = dict(
    stmt='LHEParser(cf("example/example_lhe.lhe"), 0).parse()',
    setup=std_import+"from pythiaplotter.parsers import LHEParser",
    repeat=n_repeat,
    number=n_iter
)

test_settings['heppy parser'] = dict(
    stmt='HeppyParser(cf("example/example_heppy.root"), 0).parse()',
    setup=std_import+"from pythiaplotter.parsers import HeppyParser",
    repeat=n_repeat,
    number=n_iter
)

test_settings['cmssw parser'] = dict(
    stmt='CMSSWParticleListParser(cf("example/example_cmssw.txt")).parse()',
    setup=std_import+"from pythiaplotter.parsers import CMSSWParticleListParser",
    repeat=n_repeat,
    number=n_iter
)

# EDGE based parsers
test_settings['hepmc parser'] = dict(
    stmt='HepMCParser(cf("example/example_hepmc.hepmc"), 0).parse()',
    setup=std_import+"from pythiaplotter.parsers import HepMCParser",
    repeat=n_repeat,
    number=n_iter
)

# Graphers
test_settings['node grapher'] = dict(
    stmt="assign_particles_nodes(particles)",
    setup=std_import+'from pythiaplotter.parsers import Pythia8Parser;'
                     'from pythiaplotter.graphers.node_grapher import assign_particles_nodes;'
                     '_, particles = Pythia8Parser(cf("example/example_pythia8.txt"), 0).parse()',
    repeat=n_repeat,
    number=n_iter
)

test_settings['edge grapher'] = dict(
    stmt="assign_particles_edges(particles)",
    setup=std_import+'from pythiaplotter.parsers import HepMCParser;'
                     'from pythiaplotter.graphers.edge_grapher import assign_particles_edges;'
                     '_, particles = HepMCParser(cf("example/example_hepmc.hepmc"), 0).parse()',
    repeat=n_repeat,
    number=n_iter
)

# Run tests
results_dict = {}
# raw_results_dict = {}
width = max([len(k) for k in test_settings]) + 3
print("Running benchmarks...")
for name, settings in test_settings.items():
    result = repeat(**settings)
    # raw_results_dict[name] = result
    time = min(result) / n_iter
    results_dict[name] = time
    print_result(time, name, label_width=width, comparison=previous_results)

# with open("benchmark_raw.json", "w") as f:
#     json.dump(raw_results_dict, f)

if do_comparison_store:
    with open(store, "w") as f:
        json.dump(results_dict, f)
