"""Print webpage with interactive graph."""


from __future__ import absolute_import, print_function
import json
from subprocess import PIPE, Popen
from pkg_resources import resource_string
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str


log = get_logger(__name__)


class VisPrinter(object):

    def __init__(self, output_filename="index.html", renderer="dot"):
        """

        Parameters
        ----------
        output_filename : str
            Final web page output filename
        renderer : str, optional
            Graphviz program to use for rendering layout, default is dot since dealing with DAGs
        """
        self.output_filename = output_filename
        self.renderer = renderer

    def __repr__(self):
        return generate_repr_str(self)

    def print_event(self, event, make_diagram):
        """Calculate layout, add to graph, and make website file for this event."""

        # create a graphviz suitable input
        gv = construct_gv_edges(event.graph)

        # pass to dot to get JSON output with layout co-ordinates
        raw_json = get_dot_json(gv, self.renderer)

        # update graph with layout co-ord
        add_node_positions(event.graph, raw_json)

        # parse this and create dicts suitable for vis.js
        vis_node_dicts, vis_edge_dicts = create_vis_dicts(event.graph)

        # parse this and create a new JSON suitable for vis.js
        # data_js = "test.js"
        # write_vis_json(vis_node_dicts, vis_edge_dicts, data_js)

        dkwargs = dict(indent=None, sort_keys=True)

        field_data = dict(
            title="NONE",
            nodedata=json.dumps(vis_node_dicts, **dkwargs),
            edgedata=json.dumps(vis_edge_dicts, **dkwargs),
            inputfile="blah"
        )

        # create new webpage
        write_webpage(field_data, self.output_filename)


def construct_gv_edges(graph):
    """

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    str
    """
    gv_str = ["digraph g{ rankdir=LR;ranksep=0.6;nodesep=0.4;"]
    for out_node, in_node in graph.edges_iter(data=False):
        gv_str.append("{0} -> {1};".format(out_node, in_node))
    initial = ' '.join([str(node) for node, node_data in graph.nodes_iter(data=True)
                        if node_data['initial_state']])
    gv_str.append("{{rank=same; {0} }};".format(initial))
    gv_str.append("}")
    return "".join(gv_str)


def get_dot_json(graphviz_str, renderer="dot"):
    """

    Parameters
    ----------
    graphviz_str : str
    renderer : str, optional

    Returns
    -------
    str
    """
    dot_args = [renderer, "-Tjson0"]
    p = Popen(dot_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(input=graphviz_str)
    if p.returncode != 0:
        raise RuntimeError(err)
    return out


def add_node_positions(graph, raw_json):
    """

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    raw_json : str
    """
    gv_dict = json.loads(raw_json)

    # add node positions.
    for obj in gv_dict['objects']:
        # skip not proper nodes
        if 'nodes' in obj:
            continue
        barcode = int(obj['name'])
        x, y = obj['pos'].split(',')
        x, y = float(x), float(y)
        graph.node[barcode]['pos'] = (x, y)


def create_vis_dicts(graph):
    """

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    dict, dict
    """
    node_dicts = []
    for node, node_data in graph.nodes_iter(data=True):
        node_dicts.append({
            "id": node_data['particle'].barcode,
            "label": node_data['particle'].barcode,
            "x": node_data['pos'][0],
            "y": node_data['pos'][1]
        })

    edge_dicts = []
    for out_vtx, in_vtx, edge_data in graph.edges_iter(data=True):
        edge_dicts.append({"from": out_vtx, "to": in_vtx})

    return node_dicts, edge_dicts


def write_vis_json(node_dicts, edge_dicts, json_filename):
    """Write node and edge data to JSON.

    Parameters
    ----------
    node_dicts : list[dict]

    edge_dicts : list[dict]

    json_filename : str
        Output JSON filename
    """

    with open(json_filename, "w") as f:
        f.write("var nodes = ")
        dkwargs = dict(indent=None, sort_keys=True)
        f.write(json.dumps(node_dicts, **dkwargs))
        f.write(";\n")
        f.write("var edges = ")
        f.write(json.dumps(edge_dicts, **dkwargs))
        f.write(";")


def write_webpage(field_data, output_filename):
    """Write webpage using template file and filling with user data.

    Parameters
    ----------
    field_data: dict
        Dict of template {field name: value str} to be replaced
    output_filename : str
        Output HTML filename
    """
    template = resource_string('pythiaplotter', 'printers/templates/vis_template.html')

    for k, v in field_data.items():
        template = template.replace("{{%s}}" % k, v)

    with open(output_filename, 'w') as f:
        f.write(template)
