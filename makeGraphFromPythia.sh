#!/bin/bash

# Script that converts the event listing from Pythia 
# into a Graphviz file to be plotted with dot
# e.g. 
# ./makeGraphFromPythia > myEvent.gv
# dot -Tpdf myEvent.gv -o myEvent.pdf

# Filename for output graphviz file
outputFile="myEvent.gv"
# Filename for input txt file with Pythia listing
inputFile="testLine.txt"

# array to hold names of particle for given No in event listing
nameArr=($(awk '{print $1":"$3}' $inputFile))
# Store index of first mother
m1Arr=($(awk '{print $5}' $inputFile))
# Store index of second mother
m2Arr=($(awk '{print $6}' $inputFile))
# Store index of first daughter
d1Arr=($(awk '{print $7}' $inputFile))
# Store index of second daughter
d2Arr=($(awk '{print $8}' $inputFile))

# nParticles=${#nameArr[@]}
# let "nParticles--"
echo "digraph g {" > $outputFile
echo "    rankdir = RL;" >> $outputFile
# for i in $(eval echo {0..$nParticles})
for ((i=${#nameArr[@]}-1; i>=0; i--))
# for i in {2..10}
do
	# Create string to be written to fle
	gEntry="    \"${nameArr[$i]}\" "
	
	finalState=false
	initialState=false
	
	if [[ ${nameArr[$i]} == *\(* ]]
	then
		finalState=false
	else
		finalState=true
	fi

	# Check if mother2==0 
	if [[ ${m2Arr[$i]} -eq 0 ]]
	then
		# Check if both daughters are == 0 - then initial state
		if [[ ${m1Arr[$i]} -eq 0 ]]
		then
			initialState=true
		else
			m1No=${m1Arr[$i]}
			mum=${nameArr[$m1No]}
			gEntry+="-> \"$mum\""
		fi
	else
		# Has mothers from m1 to m2 
		gEntry+="-> { "
		m1=${m1Arr[$i]}
		m2=${m2Arr[$i]}
		for m in $(eval echo {$m1..$m2})
		do
			mum=${nameArr[$m]}
			gEntry+="\"$mum\" "
		done
		gEntry+=" }"
	fi
	
	gEntry+=" [dir=\"back\"]"

	echo "$gEntry"  >> $outputFile
	
	# If initial state, make it a green box
	if [ "$initialState" == "true" ]
	then
		echo "    \"${nameArr[$i]}\" [label=\"${nameArr[$i]}\", style=filled, fillcolor=green]"  >> $outputFile
	fi

	# If final state, make it a yellow box
	if [ "$finalState" == "true" ]
	then
		echo "    \"${nameArr[$i]}\" [label=\"${nameArr[$i]}\", shape=box, style=filled, fillcolor=yellow]"  >> $outputFile
	fi
done
echo "}"  >> $outputFile