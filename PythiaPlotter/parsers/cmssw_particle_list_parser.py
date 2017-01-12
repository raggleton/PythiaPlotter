"""
Handle parsing of ParticleListDrawer as output by CMSSW.

Default is NODE representation for particles.
See example/example_cmssw.txt for example input file.

TODO: parhaps this needs a name change...
"""


import logging
from itertools import izip
from pprint import pformat
from event_classes import Event, Particle, NodeParticle
from PythiaPlotter.utils.common import map_columns
import node_grapher


log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


class CMSSWParticleListParser(object):
    """Main class to parse ParticleListDrawer as output by CMSSW"""

    def __init__(self, filename, remove_redundants=True):
        self.filename = filename
        self.remove_redundants = remove_redundants

    def parse(self):
        """Parse the file."""

        log.info("Opening event file %s" % self.filename)
        event = Event()

        with open(self.filename, 'r') as f:
            # Indicates whether to parse current line as a particle or not
            particle_line = False
            node_particles = []

            for line in f:
                line = line.strip()
                if line.startswith('[ParticleListDrawer]'):
                    continue

                if line.startswith('idx'):
                    # the lines after this line are particles, so mark this
                    # and move onto them
                    particle_line = True
                    continue

                if particle_line:
                    # check that this is a particle line - first field should
                    # be a number. If it isn't, we've finished the particle
                    # record for the event.
                    if line.split()[0].isdigit():
                        np = self.parse_particle_line(line)
                        node_particles.append(np)
                    else:
                        particle_line = False
                        break

        event.particles = [np.particle for np in node_particles]
        event.graph = node_grapher.assign_particles_nodes(node_particles,
                                                          self.remove_redundants)
        return event

    def parse_particle_line(self, line):
        """Parse line representing a particle, return a NodeParticle."""

        log.debug(line)

        # First split by |. This gives us [idx, ID-name, status,
        # parents/children, nParents/Children, pt/eta/phi, px/py/pz/m]
        # parts1 = line.strip().split('|')
        fields = ['idx', 'pdg', 'status', 'family', 'nFamily', '3mom', '4mom']
        contents = map_columns(fields, line.strip(), delim='|')

        # Get PDGID - we don't car about the name
        pdgid = contents['pdg'].strip().split()[0]

        # Get mother/daughter IDXs
        family_fields = ['parent1', 'parent2', 'child1', 'child2']
        family_contents = map_columns(family_fields, contents['family'])

        # Get pt/eta/phi
        three_mom_fields = ['pt', 'eta', 'phi']
        three_mom_contents = map_columns(three_mom_fields, contents['3mom'])

        # Get px/py/pz/m
        four_mom_fields = ['px', 'py', 'pz', 'm']
        four_mom_contents = map_columns(four_mom_fields, contents['4mom'])

        p = Particle(barcode=contents['idx'], pdgid=pdgid,
                     status=contents['status'],
                     px=four_mom_contents['px'], py=four_mom_contents['py'],
                     pz=four_mom_contents['pz'], mass=four_mom_contents['m'])
        np = NodeParticle(particle=p,
                          parent1_barcode=family_contents['parent1'],
                          parent2_barcode=family_contents['parent2'])

        log.debug(np)
        return np
