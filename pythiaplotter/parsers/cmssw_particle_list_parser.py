"""Handle parsing of ParticleListDrawer as output by CMSSW.

Default is NODE representation for particles.

See example/example_cmssw.txt for example input file.

TODO: perhaps this needs a name change...
"""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import map_columns_to_dict
from .event_classes import Event, Particle, NodeParticle


log = get_logger(__name__)


class CMSSWParticleListParser(object):
    """Main class to parse ParticleListDrawer as output by CMSSW"""

    def __init__(self, filename):
        """
        Parameters
        ----------
        filename : str
            Input filename.
        remove_redundants : bool, optional
            Remove redundant particles from the graph.
        """
        self.filename = filename

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
        event = Event(source=self.filename)

        with open(self.filename, 'r') as f:
            # Indicates whether to parse current line as a particle or not
            particle_line = False
            node_particles = []

            for line in f:
                line = line.strip()
                if line == "":
                    continue

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

        return event, node_particles

    def parse_particle_line(self, line):
        """Parse line representing a particle, return a NodeParticle."""

        log.debug(line)

        # First split by |. This gives us [idx, ID-name, status,
        # parents/children, nParents/Children, pt/eta/phi, px/py/pz/m]
        # parts1 = line.strip().split('|')
        fields = ['idx', 'pdg', 'status', 'family', 'nFamily', '3mom', '4mom']
        contents_dict = map_columns_to_dict(fields, line.strip(), delim='|')

        # Get PDGID - we don't car about the name
        pdgid = contents_dict['pdg'].strip().split()[0]

        # Get mother/daughter IDXs
        family_fields = ['parent1', 'parent2', 'child1', 'child2']
        family_contents = map_columns_to_dict(family_fields, contents_dict['family'])

        # Get pt/eta/phi
        three_mom_fields = ['pt', 'eta', 'phi']
        three_mom_contents = map_columns_to_dict(three_mom_fields, contents_dict['3mom'])

        # Get px/py/pz/m
        four_mom_fields = ['px', 'py', 'pz', 'm']
        four_mom_contents = map_columns_to_dict(four_mom_fields, contents_dict['4mom'])

        p = Particle(barcode=int(contents_dict['idx']),
                     pdgid=int(pdgid),
                     status=int(contents_dict['status']),
                     px=float(four_mom_contents['px']),
                     py=float(four_mom_contents['py']),
                     pz=float(four_mom_contents['pz']),
                     mass=float(four_mom_contents['m']))
        np = NodeParticle(particle=p,
                          parent_barcodes=list(range(int(family_contents['parent1']),
                                                     int(family_contents['parent2']) + 1)))

        log.debug(np)
        return np
