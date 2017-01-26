"""Handle parsing of LHE files.

Default is NODE representation for particles.

See example/example_lhe.lhe for example input file.
"""


from __future__ import absolute_import
from pprint import pformat
import logging
import pythiaplotter.utils.logging_config  # NOQA
# import xml.etree.ElementTree as ET  # slowwww
from lxml import etree as ET  # MegaGainz
from pythiaplotter.utils.common import map_columns_to_dict, generate_repr_str
from .event_classes import Event, Particle, NodeParticle


log = logging.getLogger(__name__)


class LHEParser(object):
    """Main class to parse a LHE file.

    User can pass in an event number to return that event (first event = 1)
    If unassigned, or no events with that event number,
    return first event in file.
    """

    def __init__(self, filename, event_num=0):
        """
        Parameters
        ----------
        filename : str
            Input filename.
        event_num : int, optional
            Index of event to parse in input file. (0 = first event)
        """
        self.filename = filename
        self.event_num = event_num
        self.events = []

    def __repr__(self):
        return generate_repr_str(self, ignore=['events'])

    def __str__(self):
        return "LHEParser: %s" % pformat(self.filename)

    def parse(self):
        """Parse contents of the input file, extract particles, and assign to a NetworkX graph.

        Returns
        -------
        Event
            Event object containing info about the event.
        list[NodeParticle]
            Collection of NodeParticles to be assigned to a graph.
        """
        log.info("Opening event file %s", self.filename)
        tree = ET.parse(self.filename)

        root = tree.getroot()

        # get tags, find index of init block, since there could be any number of
        # program-specific fields before it
        tags = [r.tag for r in root]
        try:
            init_ind = tags.index('init')
        except ValueError:
            log.exception("Cannot find <init> block in LHE file")
            raise
        self.parse_init_text(root[init_ind].text)

        # now get the event the user wanted
        event_ind = init_ind
        try:
            event_ind = tags.index('event', self.event_num)
        except ValueError:
            log.exception("Cannot find the <event> block %d in LHE file", self.event_num)
            raise

        event, node_particles = self.parse_event_text(root[event_ind].text)
        log.debug(node_particles)
        return event, node_particles

    def parse_init_text(self, text):
        """Parse the initialisation info. Currently does nothing.

        The first line is compulsory process-numer-independent info.
        Each line after represents a process

        Parameters
        ----------
        text : str
            Text in the <init></init> tags.

        Returns
        -------
        None
        """
        pass

    def parse_event_text(self, text):
        """Parse the text in a <event>...</event> block

        The first line is compulsory event info
        Each line after represents a particle.

        Parameters
        ----------
        text : str
            Event text block to be parsed.

        Returns
        -------
        Event
            Event object filled with info about the event, as well as NodeParticles in the event.
        """
        event = None
        node_particles = []
        # Keep a track of particle barcodes - start at 1, not 0.
        # LHE files do not include a barcode for each particle,
        # so we have to do it manually
        counter = 1
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            log.debug(line)

            # event info
            if not event:
                event = self.parse_event_line(line, self.event_num)
            else:
                node_particle = self.parse_particle_line(line, barcode=counter)
                node_particles.append(node_particle)
                counter += 1

        # event.particles = node_particles
        return event, node_particles

    def parse_event_line(self, line, event_num):
        """Parse a LHE event info line.

        Parameters
        ----------
        line : str
            Line of text describing the event.
        event_num : int
            Event number, as it is not included in the event line.

        Returns
        -------
        Event
            Event object with information from the line.
        """
        fields = ["num_particles", "proc_id", "weight", "scale", "aQED", "aQCD"]
        contents = map_columns_to_dict(fields, line)
        log.debug(contents)
        return Event(event_num=int(event_num))

    def parse_particle_line(self, line, barcode):
        """Parse a line that describes a particle and its mothers from a LHE file.

        Need to supply barcode to make Particle obj unique, since not supplied as
        part of LHE format

        Parameters
        ----------
        line : str
            Line of text describing a particle
        barcode : int
            Unique barcode for this particle

        Returns
        -------
        NodeParticle
            NodeParticle object that contains the Particle, as well as its mother barcodes.
        """
        fields = ["pdgid", "status", "parent1", "parent2", "col1", "col2",
                  "px", "py", "pz", "energy", "mass", "lifetime", "spin"]
        contents_dict = map_columns_to_dict(fields, line)
        p = Particle(barcode=barcode,
                     pdgid=int(contents_dict["pdgid"]),
                     status=int(contents_dict["status"]),
                     px=float(contents_dict["px"]),
                     py=float(contents_dict["py"]),
                     pz=float(contents_dict["pz"]),
                     energy=float(contents_dict["energy"]),
                     mass=float(contents_dict["mass"]))
        log.debug(contents_dict)
        np = NodeParticle(particle=p,
                          parent_barcodes=list(range(int(contents_dict['parent1']),
                                                     int(contents_dict['parent2']) + 1)))
        return np
