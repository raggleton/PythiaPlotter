"""Handle parsing of standalone Herwig output.

Default is NODE representation for particles.
"""


from __future__ import absolute_import

import re

from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import map_columns_to_dict, generate_repr_str
from .event_classes import Event, Particle, NodeParticle


log = get_logger(__name__)


class HerwigParser(object):

    def __init__(self, filename, event_num=1):
        self.filename = filename
        self.event_num = event_num

    @staticmethod
    def extract_event_num(line):
        """Get event number from line of text"""
        return int(line.split()[2])

    @staticmethod
    def is_interesting_line(line):
        """Check if a line is not one of the surplus lines"""
        line = line.strip()
        if (line.startswith(("=", "---", "Step", "*")) or "Sum of momenta" in line or line == ""):
            return False
        return True

    @staticmethod
    def line_startswith_number(line):
        return line.strip().startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))

    @staticmethod
    def get_particle_info_firstline(line):
        """Get dict of particle info for the first line of the particle"""
        parts = line.strip().split()
        pdict = {}
        # sometimes the line doesn't have a split between barcode & name e.g 91Sigma*bar0
        # so we have to take this into account for the pdgid, parents, etc
        barcode_match = re.match(r'[0-9]+', parts[0])
        if not barcode_match:
            raise RuntimeError("Cannot extract particle number. Problem line:\n%s" % line)
        pdict['barcode'] = int(barcode_match.group())
        offset = 0
        # Store the name, as sometimes Herwig uses non-conventional ones
        if parts[0] != str(pdict['barcode']):
            offset = 1
            pdict["name"] = parts[0].lstrip(str(pdict['barcode']))
        else:
            pdict["name"] = parts[1]
        pdict['pdgid'] = int(parts[2-offset])
        pdict['parent_barcodes'] = []
        # parents are in e.g. [4,6], children are in e.g. (8,9)
        if parts[3-offset].startswith("["):
            parents = parts[3-offset].strip("[").strip("]")
            if "," in parents:
                p1 = int(parents.split(",")[0])
                p2 = int(parents.split(",")[1])
                pdict['parent_barcodes'] = list(range(p1, p2+1))
            else:
                pdict['parent_barcodes'] = [int(parents)]
        return pdict

    @staticmethod
    def get_particle_info_secondline(line):
        """Get dict of particle info for the second line of the particle"""
        parts = line.strip().split()
        return {"px": float(parts[0]), "py": float(parts[1]), "pz": float(parts[2]), "E": float(parts[3])}

    def parse(self):
        """Parse the input, returning the selected event.

        Returns
        -------
        Event
            Event object containing info about the event.
        list[NodeParticle]
            Collection of NodeParticles to be assigned to a graph.
        """
        with open(self.filename) as f:
            event = Event(event_num=self.event_num)
            particles = []
            do_parsing = False
            parsing_particle = False
            current_particle_info = None
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                # Figure out if we're looking at the desired event
                if "Event number" in line:
                    if self.extract_event_num(line)-1 != self.event_num:
                        if len(particles) > 0:
                            return event, particles
                        do_parsing = False
                    else:
                        do_parsing = True

                else:
                    if not do_parsing:
                        continue

                    if not parsing_particle and not self.is_interesting_line(line):
                        continue

                    if parsing_particle:
                        current_particle_info.update(self.get_particle_info_secondline(line))
                        p = Particle(**current_particle_info)
                        p.name = current_particle_info['name']
                        np = NodeParticle(particle=p, parent_barcodes=current_particle_info['parent_barcodes'])
                        if np not in particles:
                            particles.append(np)
                        current_particle_info = None
                        parsing_particle = False

                    elif self.line_startswith_number(line):
                        current_particle_info = self.get_particle_info_firstline(line)
                        parsing_particle = True

            return event, particles
