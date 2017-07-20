"""Functions to provide TeX and normal ("raw") particle names for a given PDGID.

Uses the PDGID for TeX names, and Pythia8 for normal names.

TODO: what if pdgid doesn't exist?

TODO: deal with tex entries like: ``25 h^0 / H_1^0``
"""


from __future__ import absolute_import, print_function
import re
import xml.etree.ElementTree as ET
from pkg_resources import resource_string


def load_pdgid_dict():
    """Generate dictionary with PDGIDs and corresponding names e.g. ``\pi^0, pi0``

    For each PDGID key, we store the tex and "raw" string names,
    for both particle and antiparticle

    - Tex names taken from http://cepa.fnal.gov/psm/stdhep/numbers.shtml

    Although based on 2006 PDG, so bit out of date!
    To add new particles, either add above or in pdg_all.tex

    - String names use the ParticleData.xml file from Pythia8/xmldoc.

    Have copied it into repo, although should probably ask user to link to it.
    Although the original

    - it has lots of standard text crap before it

    - there are typos where <particle ... ends with />, not > giving error !

    So stick with mine for now...
    """
    pdgid_dict = {}

    # get latex names
    # decode() necessary as "The resource is read in binary fashion, such that the returned
    # string contains exactly the bytes that are stored in the resource."
    particle_tex = resource_string('pythiaplotter', "particledata/pdg_all.tex").decode('utf-8')
    for line in particle_tex.split('\n'):
        (pid, tex) = line.split(" ", 1)
        tex = tex.strip()
        # Generate anti-particle latex
        tex_anti = ""
        if "+" in tex:
            tex_anti = tex.replace('+', '-')
        elif "-" in tex:
            tex_anti = tex.replace("-", "+")
        else:
            # Only want the bar over the main bit of text - ignore _ or ^
            pattern = re.compile(r"[_\^]")
            stem = pattern.search(tex)
            if stem:
                tex_anti = "\\overline{%s}%s" % (tex[:stem.start()],
                                                 tex[stem.end() - 1:])
            else:
                tex_anti = "\\overline{%s}" % tex
        # add entry into dictionary, defaults for raw names = tex names
        pdgid_dict[int(pid)] = dict(tex=tex, raw=tex,)
        pdgid_dict[-1 * int(pid)] = dict(tex=tex_anti, raw=tex_anti)

    # get raw string names
    particle_data = resource_string('pythiaplotter', "particledata/PythiaParticleData.xml")
    root = ET.ElementTree(ET.fromstring(particle_data)).getroot()  # nasty hack...
    for child in root:
        pid = int(child.get('id'))
        name = child.get('name')
        # if no antiparticle name, use particle name
        anti_name = child.get('antiName') if child.get('antiName') else name
        if pid in list(pdgid_dict.keys()):
            pdgid_dict[pid]["raw"] = name
            pdgid_dict[-1 * pid]["raw"] = anti_name
        else:
            # add new entry, use raw names as defaults for tex names
            pdgid_dict[pid] = dict(tex=name, raw=name)
            pdgid_dict[-1 * pid] = dict(tex=anti_name, raw=anti_name)

    # These are for the CMSSW Pythia6 interface
    pdgid_dict[88] = dict(latex='junction', latex_anti='junction',
                          raw='junction', raw_anti='junction')
    pdgid_dict[92] = dict(latex='string', latex_anti='string',
                          raw='string', raw_anti='string')

    return pdgid_dict


# Dictionary, where PDGID is key, and value is a dictionary with fields for
# latex and raw string names. Separate entries for particle & antiparticle
PDGID_NAME_DICT = load_pdgid_dict()

# Add in custom particles e.g.
# PDGID_NAME_DICT[999] = dict(latex="I^0", latex_anti="\\overline{I}^0",
#                             raw="I0", raw_anti="I0")


def pdgid_to_tex(pdgid):
    """Convert PDGID to TeX-compatible name e.g. ``\pi^0``"""
    if int(pdgid) not in PDGID_NAME_DICT.keys():
        print("Warning, there is no name for PDGID %d" % pdgid)
        return str(pdgid)
    return PDGID_NAME_DICT[int(pdgid)]["tex"]


def pdgid_to_string(pdgid):
    """Convert PDGID to readable string (raw) name e.g. ``pi0``"""
    if int(pdgid) not in PDGID_NAME_DICT.keys():
        print("Warning, there is no name for PDGID %d" % pdgid)
        return str(pdgid)
    return PDGID_NAME_DICT[int(pdgid)]["raw"]
