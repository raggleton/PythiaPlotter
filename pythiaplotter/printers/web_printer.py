"""Print webpage with interactive graph.

This uses vis.js to do all the hard work: http://visjs.org/,
but we still use graphviz to do the layout for (a) parity with the PDF version,
(b) because it is faster, whereas web pages (so far) crash.

Of course if I could find a graphviz-as-as-JS service, that would be cooler...
"""


from __future__ import absolute_import, print_function
import json
from subprocess import PIPE, Popen
from pkg_resources import resource_string
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str
from pythiaplotter.utils.pdgid_converter import pdgid_to_string
from pythiaplotter.printers.web_config import WEB_LAYOUT_OPTS, WEB_GRAPH_OPTS, WEB_PARTICLE_OPTS


log = get_logger(__name__)


class VisPrinter(object):

    def __init__(self, opts):
        """
        Parameters
        ----------
        opts : Argparse.Namespace
            Set of options from the arg parser.

        Attributes
        ----------
        output_filename : str, optional
            Final web page output filename
        renderer : str, optional
            Graphviz program to use for rendering layout, default is dot since dealing with DAGs
        """
        self.output_filename = opts.output
        self.renderer = opts.layout

    def __repr__(self):
        return generate_repr_str(self)

    def print_event(self, event):
        """Calculate layout, add to graph nodes, and make website file for this event.

        Parameters
        ----------
        event : Event
        """

        gv_str = construct_gv_only_edges(event.graph, WEB_LAYOUT_OPTS)

        raw_json = get_dot_json(gv_str, self.renderer)

        add_node_positions(event.graph, raw_json)

        vis_node_dicts, vis_edge_dicts = create_vis_dicts(event.graph)

        pythia8status = template = resource_string('pythiaplotter', 'particledata/pythia8status.json')

        dkwargs = dict(indent=None, sort_keys=True)

        field_data = dict(
            title=event.title,
            inputfile=event.source,
            eventnum=event.event_num,
            nodedata=json.dumps(vis_node_dicts, **dkwargs),
            edgedata=json.dumps(vis_edge_dicts, **dkwargs),
            pythia8status=pythia8status
        )

        # create new webpage
        write_webpage(field_data, self.output_filename)


def construct_gv_only_edges(graph, graph_attr=None):
    """Create a graph in DOT language with just edges specified.

    This is a minimal graph, just used to determine the node positioning.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    graph_attr : dict, optional
        Graph attributes such as rankdir, nodesep

    Returns
    -------
    str
        The graph in DOT language
    """
    gv_str = ["digraph g{"]
    if graph_attr:
        for k, v in graph_attr.items():
            gv_str.append("{}={};".format(k, v))
    for out_node, in_node in graph.edges_iter(data=False):
        gv_str.append("{0} -> {1};".format(out_node, in_node))
    initial = ' '.join([str(node) for node, node_data in graph.nodes_iter(data=True)
                        if node_data['initial_state']])
    gv_str.append("{{rank=same; {0} }};".format(initial))
    gv_str.append("}")
    return "".join(gv_str)


def get_dot_json(graphviz_str, renderer="dot"):
    """Get the JSON output (with co-ords) from running a layout renderer.

    Parameters
    ----------
    graphviz_str : str
        Graph in DOT language.
    renderer : str, optional
        Renderer to use. Default is dot.

    Returns
    -------
    str
        JSON string
    """
    dot_args = [renderer, "-Tjson0"]
    p = Popen(dot_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(input=graphviz_str)
    if p.returncode != 0:
        raise RuntimeError(err)
    return out


def add_node_positions(graph, raw_json):
    """Update graph nodes with their positions, using info in `raw_json`.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to be updated
    raw_json : str
        JSON with nodes & their positions
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
    """Create list of dicts for nodes & edges suitable for input to vis.js

    This includes node position, label, hover info, etc

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    list[dict], list[dict]
        Lists of dicts corresponding to (nodes, edges)
    """
    def _generate_particle_opts(particle):
        pd = {
            'label': pdgid_to_string(particle.pdgid),
            'name': pdgid_to_string(particle.pdgid),
            'title': ""  # does tooltip, control in webpage itself
        }
        attr = particle.__dict__
        for k, v in attr.items():
            if isinstance(v, float):
                attr[k] = "%.3g" % v
        pd.update(**attr)
        return pd

    node_dicts = []
    for node, node_data in graph.nodes_iter(data=True):
        nd = {
            "id": node,
            "label": "",
            "x": node_data['pos'][0],
            "y": node_data['pos'][1]
        }
        if 'particle' in node_data:
            nd.update(_generate_particle_opts(node_data['particle']))
        node_dicts.append(nd)

    edge_dicts = []
    for out_vtx, in_vtx, edge_data in graph.edges_iter(data=True):
        ed = {"from": out_vtx, "to": in_vtx}
        if 'particle' in edge_data:
            ed.update(_generate_particle_opts(edge_data['particle']))
        edge_dicts.append(ed)

    return node_dicts, edge_dicts


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
        template = template.replace("{{%s}}" % str(k), str(v))

    with open(output_filename, 'w') as f:
        f.write(template)

    log.info("Webpage written to %s", output_filename)
