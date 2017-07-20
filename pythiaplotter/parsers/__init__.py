"""Parsers read the input file, and convert the information into a set of particles.
These can then be attached to a graph.

Attributes
----------
parser_opts : dict[str, ParserOption]
    Dictionary of all available parsers, along with info about each.
"""


from __future__ import absolute_import
from pythiaplotter.utils.logging_config import get_logger
from pythiaplotter.utils.common import generate_repr_str, check_representation_str
from .pythia8_parser import Pythia8Parser
from .hepmc_parser import HepMCParser
from .lhe_parser import LHEParser
from .cmssw_particle_list_parser import CMSSWParticleListParser
from .herwig_parser import HerwigParser


log = get_logger(__name__)


class ParserOption(object):

    def __init__(self, description, parser, default_representation, file_extension):
        """Basic class to hold info about a parser and associated fields.

        Parameters
        ----------
        description : str
            Brief description about parser

        parser : class
            The Parser class

        default_representation : {'NODE', 'EDGE'}
            Default particle representation of the parser.

        file_extension : str, optional
            Optional file extension to associate with this parser. (no preceeding .)
        """
        self.description = description
        self.parser = parser
        self.file_extension = file_extension
        check_representation_str(default_representation, "default_representation")
        self.default_representation = default_representation

    def __repr__(self):
        return generate_repr_str(self)

    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.description)


# Keys of this dict will be the commandline options for --inputFormat
parser_opts = {

    "PYTHIA": ParserOption(
        description="For screen output from Pythia 8 piped into file",
        parser=Pythia8Parser,
        file_extension=".txt",
        default_representation="NODE"
    ),

    "HEPMC": ParserOption(
        description="For HEPMC files",
        parser=HepMCParser,
        file_extension=".hepmc",
        default_representation="EDGE"
    ),

    "LHE": ParserOption(
        description="For LHE files",
        parser=LHEParser,
        file_extension=".lhe",
        default_representation="NODE"
    ),

    "CMSSW": ParserOption(
        description="For ParticleListDrawer output from CMSSW piped into file",
        parser=CMSSWParticleListParser,
        file_extension=None,
        default_representation="NODE"
    ),

    "HERWIG": ParserOption(
        description="For *.log file from running Herwig7",
        parser=HerwigParser,
        file_extension=None,
        default_representation="NODE"
    )
}

# Have to wrap the ROOT parts carefully, because it isn't installed easily with pip
try:
    from .heppy_parser import HeppyParser
    parser_opts['HEPPY'] = ParserOption(
        description="For Heppy ROOT files",
        parser=HeppyParser,
        file_extension=None,
        default_representation="NODE"
    )
except ImportError:
    log.warning("Cannot import PyROOT, no interface to Heppy tree")
