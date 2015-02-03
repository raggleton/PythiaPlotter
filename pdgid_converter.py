"""
Functions to provide TeX and normal ("raw") particle names for a given PDGID.
Uses the PDGID for TeX names, and Pythia8 for normal names.

TODO: unify into one dictionary. Rename "RawName" to "PythiaName"?
"""


import re
import xml.etree.ElementTree as ET


# Load up dictionary with PDGIDs and corresponding LaTeX names
# Taken from http://cepa.fnal.gov/psm/stdhep/numbers.shtml
# Although based on 2006 PDG, so bit out of date!
# To add new particles, either add here or in pdg_all.tex
pidTexDict = {}
with open("particledata/pdg_all.tex", "r") as particleList:
    for line in particleList:
        (key, val) = line.split(" ", 1)  # split based on 1st occurence of " "
        # print key, val,
        pidTexDict[int(key)] = val.strip()

# Load up dictionary with PDGIDs and corresponding "raw" string names
# (e.g. K_L0). Uses the ParticleData.xml file from Pythia8/xmldoc.
# Have copied it into repo, although should probably ask user to link to it.
# BUT:
#   - it has lots of standard text crap before it
#   - there are typos where <particle ... ends with />, not > giving error !
# So maybe stick with mine for now...
# For each PDGID key, there is a corresponding pair of strings,
# the first is the paricle name, the second is the antiparticle name.
ParticleDataFile = "particledata/PythiaParticleData.xml"
tree = ET.parse(ParticleDataFile)
root = tree.getroot()
pidRawDict = {}
for child in root:
    pidRawDict[int(child.get('id'))] = child.get('name'), child.get('antiName')


def pdgid_to_tex(PID):
    """Convert PDGID to TeX-compatible name e.g. \pi^0"""

    # PYTHIA makes 90 = system, not in PDG
    name = pidTexDict[abs(PID)] if PID != 90 else "PYTHIA system"

    # Remove those annoying masses in parentheses
    name = re.sub(r"\([0-9]*\)", "", name)

    # Deal with antiparticles
    if PID < 0:
        if "+" in name:
            name = name.replace('+', '-')
        elif "-" in name:
            name = name.replace("-", "+")
        else:
            # Only want the bar over the main bit of text - ignore any _ or ^
            pattern = re.compile(r"[_\^]")
            stem = pattern.search(name)
            if stem:
                name = "\\overline{"+name[:stem.start()]+"}"+name[stem.end()-1:]
            else:
                name = "\\overline{"+name+"}"
    return name


def pdgid_to_string(PID):
    """Convert PDGID to readable string (raw) name e.g. pi0"""
    PID = int(PID)
    name = pidRawDict[abs(PID)][0] if PID > 0 else pidRawDict[abs(PID)][1]
    return name
