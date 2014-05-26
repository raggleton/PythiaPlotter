# Script that converts the event listing from Pythia 
# into a Graphviz file to be plotted with dot
# e.g. 
# python makeGraphFromPythia.py
# dot -Tpdf myEvent.gv -o myEvent.pdf

# Edit the following:

# Filename for output graphviz file
outputFile = open("myEvent.gv","w")

# Filename for input txt file with Pythia listing
inputFile = open("testLine.txt","r")

# Interesting particles we wish to highlight
# include antiparticles
interesting = [ "tau+", "tau-", "mu+", "mu-" ]

############################################################################
# DO NOT EDIT ANYTHING BELOW HERE
############################################################################

class Particle:
	'Class to hold particle info in an event listing'
	number         = -1 # number in event listing
	PID            = -1 # PDGID value
	name           = "" # particle name e.b nu_mu
	status         = 0  # status of particle. If > 0 , is final state.
	m1             = 0 # number of mother 1
	m2             = 0 # number of mother 2
	mothers        = [] # list of Particle objects that are its mother
	daughters      = [] # list of Particle objects that are its mother
	isInitialState = False # Whether initial state or not
	isFinalState   = False # Whether final state or not

	def __init__(self, number, PID, name, status, m1, m2):
		self.number = number
		self.PID    = PID
		self.name   = name
		self.status = status
		self.m1     = m1
		self.m2     = m2
		
		if (status > 0):
			self.isFinalState = True
		
		if ((m1 == 0) and (m2 == 0)):
			self.isInitialState = True
		
		# Sometimes Pythia sets m2 == 0 if only one mother
		# This causes looping issues, so set m2 = m1 if that's the case
		if ((m1 != 0) and (m2 == 0)):
			self.m2 = m1

	def addMother(self, mother):
		self.mothers.append(mother)

	def addDaughter(self, daughter):
		self.daughters.append(daughter)

	def nMothers(self):
		return len(self.mothers)
	
	def nDaughters(self):
		return len(self.daughters)

# List of Particle objects in event, in order of number in event listing
# So the object at event[i] has number = i
event = []

# Read in file to array (of objects?)
for line in inputFile:
	values   = line.split()
	number   = values[0]
	PID      = values[1]
	name     = values[2]
	status   = values[3]
	m1       = int(values[4])
	m2       = int(values[5])
	particle = Particle(number, PID, name, status, m1, m2)
	
	event.append(particle)

# Add references to mothers
for p in event:
	for m in range(p.m1,p.m2+1):
		print event[m].name
		p.mothers.append(event[m])

# To hold all the initial state event that should be aligned
sameOnes = []

# 