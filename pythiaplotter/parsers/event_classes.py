"""Classes to describe event & physical particles, as well as four-vectors."""


from __future__ import absolute_import, division
import math
import networkx as nx
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str, get_terminal_width
from functools import total_ordering


log = get_logger(__name__)


class Event(object):
    """Hold event info"""

    def __init__(self, event_num=0, **kwargs):
        self.event_num = int(event_num)
        self.graph = None  # to hold NetworkX graph
        self.__dict__.update(**kwargs)

    def __repr__(self):
        ignore = ["graph"]
        return generate_repr_str(self, ignore)

    def __str__(self):
        """Print event info in format suitable for use on graph or printout"""
        ignore = ["graph"]
        info = [k + ": " + str(v) + "\n" for k, v in self.__dict__.items() if k not in ignore]
        return "Event:\n{0}".format("".join(info))

    def print_stats(self):
        """Print some basic statistics about the event"""
        log.info("Some statistics:")
        log.info("----------------")
        log.info(nx.info(self.graph))
        log.info("Graph density {}".format(nx.density(self.graph)))
        log.info("Histogram of node degree:")
        # Deal with bin contents larger than the terminal width by scaling bins
        bin_contents = nx.degree_histogram(self.graph)
        tw = get_terminal_width()
        offset = 5  # for bin labels, etc
        if max(bin_contents) > (tw - offset):
            scale = (tw - offset) / max(bin_contents)
            bin_contents = [int(round(b*scale)) for b in bin_contents]
        for i, h in enumerate(bin_contents):
            log.info("{:2d} {}".format(i, "#"*h))


@total_ordering
class Particle(object):

    def __init__(self, barcode, pdgid=0, status=0,
                 initial_state=False, final_state=False, **kwargs):
        """Hold information about a particle in an event.

        Parameters
        ----------
        barcode : int
            Unique integer for this particle to identify it in an event.
        pdgid : int, optional
            PDGID code for this particle, see PDG
        status : int, optional
            Status code for the particle. NB conventions differ between generators
        initial_state : bool, optional
            Flag initial state particle (no parents)
        final_state : bool, optional
            Flag final state particle (no children)
        kwargs : dict
            Store any other particle attributes, such as px/py/pz/pt/energy/mass
        """
        self.barcode = int(barcode)
        self.pdgid = int(pdgid)
        self.status = int(status)
        self.final_state = final_state
        self.initial_state = initial_state
        self.event = None  # parent event
        self.__dict__.update(**kwargs)
        if all([k in kwargs for k in ['px', 'py', 'pz']]):
            pt, eta, phi = convert_px_py_pz(float(self.px), float(self.py), float(self.pz))
            self.__dict__['pt'] = pt
            self.__dict__['eta'] = eta
            self.__dict__['phi'] = phi

    def __repr__(self):
        ignore = ['event']
        return generate_repr_str(self, ignore)

    def __str__(self):
        # Properties to print out - we don't want all of them!
        return "Particle {0}, PDGID {1}".format(self.barcode, self.pdgid)

    def __eq__(self, other):
        return self.barcode == other.barcode

    def __lt__(self, other):
        return self.barcode < other.barcode


def convert_px_py_pz(px, py, pz):
    """Convert cartesian momentum components :math:`p_x, p_y, p_z` into :math:`p_T, \eta, \phi`

    Notes
    -----
    * pt (:math:`p_T`) is the momentum in the transverse (x-y) plane
    * eta (:math:`\eta`) is the pseudorapidity, :math:`\eta = -\ln(\\tanh(\\theta/2))`
      where :math:`\\theta` is the angle of the 3-momentum in the x-z plane relative to the z axis
    * phi (:math:`\phi`) is the angle of the 3-momentum in the x-y plane relative to the x axis

    Relationships between :math:`p_T, \eta, \phi` and :math:`p_x, p_y, p_z`:

    .. math::

        p_x &= p_T * \cos(\phi)

        p_y &= p_T * \sin(\phi)

        p_z &= p_T * \sinh (\eta) = p * \cos(\\theta)

    Note that if :math:`p_T = 0`, :math:`\eta = \mathrm{sign}(p_z) * \infty`.

    Parameters
    ----------
    px, py, pz : float
        Cartesian component of momentum along x, y, z axis, respectively

    Returns
    -------
    pt, eta, phi : float
        Transverse momentum, pseudorapidity, and azimuthal angle (in radians).
    """
    # transverse momentum
    pt = math.sqrt(math.fsum([math.pow(px, 2), math.pow(py, 2)]))
    # total momentum
    p = math.sqrt(math.fsum([math.pow(pt, 2), math.pow(pz, 2)]))
    if pt != 0:
        eta = math.asinh(pz / pt)
        phi = math.asin(py / pt)
    else:
        eta = math.copysign(float('inf'), pz)
        phi = 0
    return pt, eta, phi


class NodeParticle(object):

    def __init__(self, particle, parent_barcodes):
        """Class to hold info when particle is represented by a node.

        Parameters
        ----------
        particle : Particle
            The particle of interest
        parent_barcodes : list[int]
            List of parent barcodes
        """
        self.particle = particle
        self.parent_barcodes = parent_barcodes

    def __repr__(self):
        return generate_repr_str(self)

    @property
    def barcode(self):
        return self.particle.barcode


class EdgeParticle(object):
    """Class to hold info when particle is represented by an edge.

    This contains the physical Particle object, and associated info that
    is edge-specific, such as incoming/outgoing vertex barcodes.

    Vertex barcodes are ints.
    """

    def __init__(self, particle, vtx_in_barcode, vtx_out_barcode):
        self.particle = particle
        self.vtx_in_barcode = int(vtx_in_barcode)
        self.vtx_out_barcode = int(vtx_out_barcode)

    @property
    def barcode(self):
        return self.particle.barcode

    def __repr__(self):
        return generate_repr_str(self)
