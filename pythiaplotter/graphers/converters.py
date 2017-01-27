"""Functions to do conversions between particle representations."""


from __future__ import absolute_import
import logging
import pythiaplotter.utils.logging_config  # NOQA
import copy
import networkx as nx
from pythiaplotter.parsers.event_classes import NodeParticle, EdgeParticle
from .node_grapher import assign_particles_nodes
from .edge_grapher import assign_particles_edges


log = logging.getLogger(__name__)


def edge_to_node(graph):
    """Converts graph from edge to node representation.

    1) Create a node for each particle edge
    2) Add directed edges between all combinations of incoming & outgoing particles at a vertex

    Since there is a 1:1 correspondence between the node and edge particles,
    we can use the assign_particles_nodes() function to do this,
    so long as we construct our NodeParticles correctly.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    NetworkX.MultiDiGraph
    """
    node_particles = []
    for out_node, in_node, edge_data in graph.edges_iter(data=True):
        particle = edge_data['particle']
        parent_barcodes = [data['particle'].barcode for _, _, data
                           in graph.in_edges_iter(out_node, data=True)]
        np = NodeParticle(particle, parent_barcodes)
        node_particles.append(np)
    return assign_particles_nodes(node_particles)


def node_to_edge(graph):
    """Converts graph from node to edge representation.

    This conversion is more comples, and there is not always a simple 1:1 correspondence.
    Briefly:

    1) Determine if certain parent-child relationships require a duplicate parent node to be
    inserted inbetween.

    2) Turn each node into a directed edge with outgoing and incoming vertices, ensuring that
    all particles incoming (parents) & outgoing (children) from the same vertex have the same
    vertex barcode.

    3) Connect all edges together into a graph.

    The last step is done by passing a list of EdgeParticle s to assign_particle_edges(), thereby
    avoiding duplication.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph


    Returns
    -------
    NetworkX.MultiDiGraph
    """

    graph_with_duplicates = insert_duplicate_nodes(graph)
    edge_particles = construct_edges_from_nodes(graph_with_duplicates)
    graph_edge = assign_particles_edges(edge_particles)

    return graph_edge


def insert_duplicate_nodes(graph):
    """Create a copy of the graph with duplicate parent nodes inserted when child has
    non-common shared parentage.

    This can happen when a subgraph of parent and child nodes has some child nodes that do not
    have all the same parents, and therefore duplicate nodes would be required to split the
    subgraph into multiple graphs where all the children do have the same parents.

    Duplicate parents have the same Particle as the parent, but with a barcode starting 20xxxx.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to analyze

    Returns
    -------
    NetworkX.MultiDiGraph
        Copy of input graph but with duplicate parent nodes added.
    """
    nodes_done = []
    graph_copy = graph.copy()

    for node in graph.nodes_iter():
        if node in nodes_done or len(graph.successors(node)) == 0:
            continue

        log.debug("Doing node %d", node)

        parents, children = get_related_parents_children(graph, node)

        if duplication_needed(graph, parents, children):
            # For each shared parent, add a duplicate node between
            # it and a child with shared parentage
            for pa in parents:
                log.debug("Parent %d", pa)
                these_children = graph.successors(pa)
                # Skip if only 1 child
                if len(these_children) <= 1:
                    continue

                for ch in these_children:
                    log.debug("Child %d", ch)

                    # Skip children with only 1 parent - no shared parentage, no duplication needed
                    if len(graph.predecessors(ch)) <= 1:
                        log.debug("Skipping %d", ch)
                        continue

                    # remove parent - child connection
                    graph_copy.remove_edge(pa, ch)
                    parent_particle = graph.node[pa]['particle']

                    # create duplicate particle and add it in with a new unique barcode
                    dupl_particle = copy.deepcopy(parent_particle)
                    new_barcode = 20000 + parent_particle.barcode  # assumes graph has <20K nodes...
                    # do a check for uniqueness
                    while new_barcode in graph_copy:
                        new_barcode += 1
                    dupl_particle.barcode = new_barcode

                    graph_copy.add_node(new_barcode, particle=dupl_particle,
                                        initial_state=False, final_state=False)
                    graph_copy.add_edge(pa, new_barcode)
                    graph_copy.add_edge(new_barcode, ch)

                    log.debug("Adding duplicate %d", new_barcode)
                    log.debug("Adding %d -> %d -> %d", pa, new_barcode, ch)

        nodes_done.extend(parents)

    return graph_copy


def get_related_parents_children(graph, node):
    """Returns nodes indices of all children and their parents related to a node.

    This includes:

    - the children of the node
    - all other parents of those children
    - all of those childens parents
    - all of those parents children
    - ...

    recursviely until we are done. Thus we obtain all nodes in this generation or 1 later, which
    are connected without straying outside of those two generations
    (ignoring the directionality of edges for a moment)

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
        Graph to analyze
    node : int
        Node to consider

    Returns
    -------
    all_parents : list[int]
        All connected parents
    all_children : list[int]
        All connected children

    """
    all_children = graph.successors(node)
    all_parents = [node]
    log.debug("start related parents: %s", all_parents)
    log.debug("start related children: %s", all_children)
    # iterative algo to get all unique parents and children
    while (set(all_parents) != set(get_all_parents(graph, all_children))
           or set(all_children) != set(get_all_children(graph, all_parents))):

        all_parents.extend(list(set(get_all_parents(graph, all_children)) - set(all_parents)))
        all_children.extend(list(set(get_all_children(graph, all_parents)) - set(all_children)))

    log.debug("end related parents: %s", all_parents)
    log.debug("end related children: %s", all_children)
    return all_parents, all_children


def get_all_parents(graph, children):
    """Get all unique parents nodes of all specified children nodes in a flattened list.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    children : list[int]

    Returns
    -------
    list[int]
        Parent nodes
    """
    return list(set([p for c in children for p in graph.predecessors(c)]))


def get_all_children(graph, parents):
    """Get all unique child nodes of all specified parent nodes in a flattened list.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    parents : list[int]

    Returns
    -------
    list[int]
        Child nodes
    """
    return list(set([c for p in parents for c in graph.successors(p)]))


def duplication_needed(graph, parents, children):
    """For a set of parent and child nodes in a graph, determine if any duplicate nodes are needed.

    This can happen when a subgraph of parent and child nodes has some child nodes that do not
    have all the same parents, and therefore duplicate nodes would be required to split the
    subgraph into multiple graphs where all the children do have the same parents.

    Example
    -------
    For a graph with edges [(1, 3), (1, 4), (2, 4), (2, 5)], nodes 1 and 2 are the parents,
    and nodes 3, 4, 5 are the children. 3 and 5 have one parent each (1 and 2, repsectively),
    but 4 has 2 parents. This would cause us issues when inserting edges in lieu of nodes.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph
    parents : list[int]
    children : list[int]

    Returns
    -------
    bool
    """
    return any([len(graph.predecessors(c)) != len(parents) for c in children])


def construct_edges_from_nodes(graph):
    """Convert each node (representing a NodeParticle) into a EdgeParticle, with vertex barcodes.

    To do this, we have to ensure that a particle's incoming & outgoing vertices are concistent
    with its children & parents. Thus we ask them first for a suitable vertex,
    and if none can be found, create a new vertex barcode.

    Parameters
    ----------
    graph : NetworkX.MultiDiGraph

    Returns
    -------
    list[EdgeParticle]

    Raises
    ------
    IndexError
        If there is more than one unique candidate in/out vertex barcode.
    """
    edge_particles = []
    vtx_barcodes = set()

    def _find_outgoing_vtx_barcode(graph, node):
        """Find a suitable outgoing vertex, using parent's incoming if possible."""
        parent_nodes = graph.predecessors(node)
        if len(parent_nodes) != 0:
            parent_in = set([graph.node[p]['in_vtx'] for p in parent_nodes
                             if 'in_vtx' in graph.node[p]])
            sibling_out = set([graph.node[s]['out_vtx']
                               for s in get_all_children(graph, graph.predecessors(node))
                               if 'out_vtx' in graph.node[s]])
            vtx = parent_in | sibling_out
            if len(vtx) > 1:
                raise IndexError("Too many possibilities for outgoing barcode")
            elif len(vtx) == 1:
                return vtx.pop()
        return None

    def _find_incoming_vtx_barcode(graph, node):
        """Find a incoming vertex, using children's outgoing if possible."""
        child_nodes = graph.successors(node)
        if len(child_nodes) != 0:
            children_out = set([graph.node[c]['out_vtx'] for c in child_nodes
                                if 'out_vtx' in graph.node[c]])
            sibling_in = set([graph.node[s]['in_vtx']
                              for s in get_all_parents(graph, graph.successors(node))
                              if 'in_vtx' in graph.node[s]])
            vtx = children_out.union(sibling_in)
            if len(vtx) > 1:
                raise IndexError("Too many possibilities for incoming barcode")
            elif len(vtx) == 1:
                return vtx.pop()
        return None

    for node, data in graph.nodes_iter(data=True):
        log.debug("Constructing EP for node %d", node)
        # Figure out the outgoing vertex barcode, use parent's incoming one if there is a parent,
        # or any sibling outgoing one. Otherwise create unique one.
        ob = _find_outgoing_vtx_barcode(graph, node) or len(vtx_barcodes)
        vtx_barcodes.add(ob)

        # Figure out the incoming vertex barcode, use children's outgoing one if there are any,
        # or any sibling incoming one. Otherwise create unique one.
        ib = _find_incoming_vtx_barcode(graph, node) or len(vtx_barcodes)
        vtx_barcodes.add(ib)

        # store the particles in/out vertex barcode to connect other children to parents later
        graph.node[node]['out_vtx'] = ob
        graph.node[node]['in_vtx'] = ib
        ep = EdgeParticle(particle=data['particle'], vtx_in_barcode=ib, vtx_out_barcode=ob)
        log.debug("Adding EdgeParticle %s", ep)
        edge_particles.append(ep)

    return edge_particles
