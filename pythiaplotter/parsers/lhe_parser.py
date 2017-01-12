"""
Handle parsing of LHE files.

Default is NODE representation for particles.
See example/example_lhe.lhe for example input file.
"""

import logging
from pprint import pformat
# import xml.etree.ElementTree as ET  # slowwww
from lxml import etree as ET  # MegaGainz
from event_classes import Event, Particle, NodeParticle
import pythiaplotter.graphers.node_grapher as node_grapher
from pythiaplotter.utils.common import map_columns


log = logging.getLogger(__name__)


class LHEParser(object):
    """Main class to parse a LHE file.

    User can pass in an event number to return that event (first event = 1)
    If unassigned, or no events with that event number,
    return first event in file.
    """

    def __init__(self, filename, event_num=0, remove_redundants=True):
        self.filename = filename
        self.event_num = event_num
        self.remove_redundants = remove_redundants
        self.events = []

    def __repr__(self):
        return "%s.%s(filename=%r, event_num=%d, remove_redundants=%s)" % (
            self.__module__,
            self.__class__.__name__,
            self.filename,
            self.event_num,
            self.remove_redundants)

    def __str__(self):
        return "LHEParser: %s" % pformat(self.filename)

    def parse(self):
        """Parse LHE file, returning an Event object with list of Particles
        assigned to a graph in NODE representation

        """
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
            log.exception("Cannot find the <event> block %d in LHE file" % self.event_num)
            raise

        event = self.parse_event_text(root[event_ind].text)
        log.debug(event.particles)
        event.graph = node_grapher.assign_particles_nodes(event.particles, self.remove_redundants)
        return event

    def parse_init_text(self, text):
        """Parse the initialisation info.

        The first line is compulsory process-numer-independent info.
        Each line after represents a process
        """
        pass

    def parse_event_text(self, text):
        """Parse the text in a <event>...</event> block

        The first line is compulsory event info
        Each line after represents a particle.
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

        event.particles = node_particles
        return event

    def parse_event_line(self, line, event_num):
        """Parse a LHE event info line"""
        fields = ["num_particles", "proc_id", "weight", "scale", "aQED", "aQCD"]
        contents = map_columns(fields, line)
        log.debug(contents)
        return Event(event_num=event_num)

    def parse_particle_line(self, line, barcode):
        """Parse a LHE particle line

        Returns a NodeParticle object

        Need to supply barcode to make Particle obj unique, not supplied as
        part of LHE format
        """
        fields = ["pdgid", "status", "parent1", "parent2", "col1", "col2",
                  "px", "py", "pz", "energy", "mass", "lifetime", "spin"]
        contents = map_columns(fields, line)
        log.debug(contents)
        p = Particle(barcode=barcode,
                     pdgid=contents["pdgid"],
                     px=contents["px"],
                     py=contents["py"],
                     pz=contents["pz"],
                     energy=contents["energy"],
                     mass=contents["mass"],
                     status=contents["status"])
        np = NodeParticle(particle=p,
                          parent1_barcode=int(contents['parent1']),
                          parent2_barcode=int(contents['parent2']))
        return np
