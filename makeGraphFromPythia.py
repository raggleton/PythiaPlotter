# Script that converts the event listing from Pythia 
# into a Graphviz file to be plotted with dot
# e.g. 
# python makeGraphFromPythia.py
# dot -Tpdf myEvent.gv -o myEvent.pdf

############################################################################
# Edit the following:
############################################################################
#
# Filename for output graphviz file
outputFilename = "myEvent2.gv"
#
# Filename for input txt file with Pythia listing
inputFilename = "testLine.txt"
#
# Interesting particles we wish to highlight
# include antiparticles
interesting = [ "tau+", "tau-", "mu+", "mu-" ]
#
############################################################################
# DO NOT EDIT ANYTHING BELOW HERE
############################################################################

class Particle:
	'Class to hold particle info in an event listing'

	def __init__(self, number, PID, name, status, m1, m2):
		# Class instance variables
		self.number         = number # number in event listing
		self.PID            = PID  # PDGID value
		self.name           = name # particle name e.b nu_mu
		self.status         = status # status of particle. If > 0 , is final state.
		self.m1             = m1 # number of mother 1
		self.m2             = m2 # number of mother 2
		self.skip           = False # Whether to skip when writing nodes to file
		self.mothers        = [] # list of Particle objects that are its mother
		self.daughters      = [] # list of Particle objects that are its mother
		self.isInteresting  = False # Whether this is one of the particles the user wants highlighted
		self.isFinalState   = False
		self.isInitialState = False

		if (status > 0):
			self.isFinalState = True
		
		if ((m1 == 0) and (m2 == 0)):
			self.isInitialState = True
		
		# Sometimes Pythia sets m2 == 0 if only one mother & particle from shower
		# This causes looping issues, so set m2 = m1 if that's the case
		if ((m1 != 0) and (m2 == 0)):
			self.m2 = m1

		if self.name.translate(None, '()') in interesting:
			self.isInteresting = True

	def getRawName(self):
		# Get name without any ( or )
		return self.name.translate(None, '()')

############################################################################
# MAIN BODY OF CODE HERE
############################################################################

# List of Particle objects in event, in order of number in event listing
# So the object at event[i] has self.number = i
event = []

# To hold all the initial state particles that should be aligned
sameInitialOnes = []

# Open inut/output files
outFile   = open(outputFilename,"w")
inputFile = open(inputFilename,"r")

# Read in file to list of Particles
for line in inputFile:
	values   = line.split()
	number   = int(values[0])
	PID      = int(values[1])
	name     = values[2]
	status   = int(values[3])
	m1       = int(values[4])
	m2       = int(values[5])
	particle = Particle(number, PID, name, status, m1, m2)

	if particle.isInitialState:
		sameInitialOnes.append(particle)

	event.append(particle)


# Add references to mothers
for p in event:
	for m in range(p.m1,p.m2+1):
		p.mothers.append(event[m])

# Now process all the particles and add appropriate links to graphviz file
# Start from the end and work backwards to pick up all connections 
# (doesn't work if you start at beginning and follow daughters)
outFile.write("digraph g {\n    rankdir = RL;\n")
for p in reversed(event):
	# if p.number < 901:	
	if p.skip:
		continue

	pNumName = '"%s:%s"' % (p.number, p.name)
	entry = '    %s -> { ' % pNumName
	
	for m in p.mothers:
		entry += '"%s:%s" ' % (m.number, m.name)

	entry += "} [dir=\"back\"]\n"
	
	print entry
	outFile.write(entry)
	
	# Define special features for initial, final state and interesting particles
	# Final state: box, yellow fill
	# Initial state: circle (default), green fill
	# Interesting: red fill (overrides green/yellow fill)
	conf = ""
	if p.isInteresting:
		conf = '    %s [label=%s, shape=box, style=filled, fillcolor=red]\n' % (pNumName, pNumName)
	else:
		if p.isFinalState:
			conf = '    %s [label=%s, shape=box, style=filled, fillcolor=yellow]\n' % (pNumName, pNumName)
		elif p.isInitialState:
			conf = '    %s [label=%s, shape=box, style=filled, fillcolor=green]\n' % (pNumName, pNumName)

	if conf:
		outFile.write(conf)
		print conf


# Set all initial particles to be level in diagram
rank = "    {rank=same;"
for s in sameInitialOnes:
	rank += '"%s:%s" ' % (s.number, s.name)
outFile.write(rank+"} // Put initial particles on same level\n")

outFile.write("}")

# Clean up
inputFile.close()
outFile.close()