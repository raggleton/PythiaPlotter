import re

# Load up dictionary with PDGIDs and corresponding LaTeX names
# Taken from http://cepa.fnal.gov/psm/stdhep/numbers.shtml
# Although based on 2006 PDG, so bit out of date!
# To add new particles, either add here or in pdg_all.tex
pidDict = {}
with open("pdg_all.tex", "r") as particleList:
	for line in particleList:
		(key, val) = line.split(" ",1) # split based on first occurence of " "
		# print key, val,
		pidDict[int(key)] = val.strip()

# This converts from PDGID (see ) and returns a Latex form for the name,
# also deals with antiparticles
def convertPIDToName(PID):
	name = pidDict[abs(PID)]
	if PID < 0:
		if "+" in name:
			name = name.replace('+', '-')
		elif "-" in name:
			name = re.sub('-', r'+', name)
		else:
			# Only want the bar over the main bit of text - ignore any _ or ^
			pattern = re.compile(r"[_\^]")
			stem = pattern.search(name)
			if stem: 
				name = "\\overline{"+name[:stem.start()]+"}"+name[stem.end()-1:]
			else:
				name = "\\overline{"+name+"}"
	return name
