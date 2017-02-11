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


# Settings for particles using the dot printer
DOT_PARTICLE_OPTS = [
    # Example for b quarks
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
    # Example for muons, taus
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
    # Example for gluons
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
    # Example for photons
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
