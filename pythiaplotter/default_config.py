"""This file contains the default settings for parsers and printers."""


from __future__ import absolute_import, division


# Settings for the entire graph
GRAPH_OPTS = {
    "rankdir": "LR",
    "ranksep": 0.6,
    "nodesep": 0.6,
    # These 3 only apply to the DOT printer
    "labelloc": "top",
    "labeljust": "left",
    "label": r'<<FONT POINT-SIZE="45"><B>${title}<br/>${source}<br/>event ${event_num}</B></FONT><br/><FONT POINT-SIZE="35">All energies in GeV</FONT>>'
}


# Settings for particle labels for the DOT printer
# Uses the python .format() method.
# Any particle field name can be used in the {} specifiers, e.g. {pt}
#
# There separate dicts for NODE and EDGE representations,
# and for each a "fancy" label (e.g for PDF output), and "plain" label
# (e.g for postscript output).
DOT_LABEL_OPTS = {
    "node": {
        "fancy": r"<{barcode}: {name}, p<SUB>T</SUB>: {pt:.2f}<br/>&eta;: {eta:.2f},  &phi;: {phi:.2f}<br/>status: {status}>",
        "plain": '"{barcode}: {name}, pT: {pt:.2f}, eta: {eta:.2f}, phi: {phi:.2f}"'
    },
    "edge": {
        "fancy": r"<{barcode}: {name}, p<SUB>T</SUB>: {pt:.2f}<br/>&eta;: {eta:.2f},  &phi;: {phi:.2f}<br/>status: {status}>",
        "plain": '"{barcode}: {name}, pT: {pt:.2f}, eta: {eta:.2f}, phi: {phi:.2f}"'
    }
}


# Settings for particle styling using the DOT printer
# Each entry must be a dict, with 2 fields: "filter" and "attr".
# "filter" must hold a lambda, that takes in a particle and returns a bool.
# If this evaluates True, the styling will be used.
# The "attr"" field must hold a dict, with keys "node" and "edge".
# The "node" dict is used for NODE particle representation, and similarly
# the "edge" dict for EDGE representation.
# Each of these holds a dict, with graphviz key : values.
# Possible keys and values can be found here:
#
DOT_PARTICLE_OPTS = [
    # Style b quarks
    dict(
        filter=lambda p: abs(p.pdgid) == 5,
        attr={
            "node": {
                "style": "filled",
                "color": "red"
            },
            "edge": {
                "color": "red",
                "fontcolor": "red"
            }
        }
    ),
    # Style muons, taus
    dict(
        filter=lambda p: abs(p.pdgid) in [13, 15],
        attr={
            "node": {
                "style": "filled",
                "color": "purple"
            },
            "edge": {
                "color": "purple",
                "fontcolor": "purple",
                "penwidth": 4
            }
        }
    ),
    # Style gluons
    dict(
        filter=lambda p: abs(p.pdgid) == 21,
        attr={
            "node": {
                "style": "filled",
                "color": "grey"
            },
            "edge": {
                "color": "grey",
                "fontcolor": "grey"
            }
        }
    ),
    # Style photons
    dict(
        filter=lambda p: abs(p.pdgid) == 22,
        attr={
            "node": {
                "style": "filled",
                "color": "cadetblue1"
            },
            "edge": {
                "color": "cadetblue1",
                "fontcolor": "cadetblue1"
            }
        }
    ),

    # Default for initial-state particles
    dict(
        filter=lambda p: p.initial_state,
        attr={
            "node": {
                "style": "filled",
                "shape": "circle",
                "color": '"#00cd00"'
            },
            "edge": {
                "color": '"#00cd00"',
                "fontcolor": '"#00cd00"',
                "penwidth": 5
            }
        }
    ),

    # Default for final-state particles
    dict(
        filter=lambda p: p.final_state,
        attr={
            "node": {
                "style": "filled",
                "shape": "box",
                "color": "dodgerblue1"
            },
            "edge": {
                "color": "dodgerblue1",
                "fontcolor": "dodgerblue1"
            }
        }
    ),
    # Default for all particles
    dict(
        filter=lambda p: True,
        attr={
            "node": {},
            "edge": {
                "penwidth": 2
            }
        }
    )
]
