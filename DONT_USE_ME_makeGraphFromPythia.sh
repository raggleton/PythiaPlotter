#!/bin/bash

# Script that converts the event listing from Pythia 
# into a Graphviz file to be plotted with dot
# e.g. 
# ./makeGraphFromPythia.sh
# dot -Tpdf myEvent.gv -o myEvent.pdf

# Filename for output graphviz file
outputFile="myEvent.gv"
# Filename for input txt file with Pythia listing
inputFile="testLine.txt"

# Array to hold number&names of particle for given No in event listing
NumNameArr=($(awk '{print $1":"$3}' $inputFile))
# Array to hold particle names by themselves ofr given No in event listing
NameArr=($(awk '{print $3}' $inputFile))
# Store index of first mother
m1Arr=($(awk '{print $5}' $inputFile))
# Store index of second mother
m2Arr=($(awk '{print $6}' $inputFile))
# Store index of first daughter
# d1Arr=($(awk '{print $7}' $inputFile))
# Store index of second daughter
# d2Arr=($(awk '{print $8}' $inputFile))


# Interesting particles we wish to highlight
# include antiparticle
interesting=( "tau+" "tau-" "mu+" "mu-" )

# To hold all the initial state particles that should be aligned
sameOnes=""

# To hold all the particles that should be skipped
skipList=( "" )

echo "digraph g {" > $outputFile
echo "    rankdir = RL;" >> $outputFile
for ((i=${#NumNameArr[@]}-1; i>=0; i--))
# for i in {2..10}
do
	# Check whether in skip list	
	skip="false"
	for s in "${skipList[@]}"
	do
		if [[ ${NameArr[$i]} == "$s" ]]
		then
			skip=true
		fi
	done

	# If not in skip list, look at particle entry
	if [[ $skip == "false" ]]
	then

		# Create string to be written to fle
		gEntry="    \"${NumNameArr[$i]}\" "
		
		finalState=false
		initialState=false
		
		# Check if final-state or not: 
		# non final state are named "(mu+)", final state are "mu+""
		if [[ ${NumNameArr[$i]} == *\(* ]]
		then
			finalState=false
		else
			finalState=true
		fi

		# Check if both mothers are == 0 - then initial state
		if [[ ${m1Arr[$i]} -eq 0 ]]
		then
			initialState=true
			sameOnes+="\"${NumNameArr[$i]}\" "
		# Check if mother2==0 & final state
		elif [[ ${m2Arr[$i]} -eq 0 ]]
		then
				m1No=${m1Arr[$i]}
				mum=${NumNameArr[$m1No]}
				gEntry+="-> \"$mum\""
		# Check to see if it is a redundant particle (either m2 == 0, or m1=m2)
		# elif [[ ${m1Arr[$i]} -eq 0 ]]
		# then
		# || (${m1Arr[$i]} -eq ${m2Arr[$i]}) ]]
			#statements
			echo "redundant"
		else
			# Satisfied it isn't a redundant, initial or final-state particle

			# Has mothers from m1 to m2 
			gEntry+="-> { "
			m1=${m1Arr[$i]}
			m2=${m2Arr[$i]}
			for m in $(eval echo {$m1..$m2})
			do
				mum=${NumNameArr[$m]}
				gEntry+="\"$mum\" "
			done
			gEntry+=" }"
		fi
		
		# Reverse arrow direction, since we link daughters to mothers
		gEntry+=" [dir=\"back\"]"

		echo "$gEntry"  >> $outputFile
		
		# Check to see if one of the interesting particles we defined above
		isInteresting=false
		for p in "${interesting[@]}"
		do
			if [[ ${NameArr[$i]} == *"$p"* ]]
			then
				isInteresting=true
			fi
		done

		if [[ $isInteresting == "true" ]]
		then
			# If final state, make it a square box
			if [ "$finalState" == "true" ]
			then
				echo "        \"${NumNameArr[$i]}\" [label=\"${NumNameArr[$i]}\", shape=box, style=filled, fillcolor=red]"  >> $outputFile
			else
				echo "        \"${NumNameArr[$i]}\" [label=\"${NumNameArr[$i]}\", style=filled, fillcolor=red]"  >> $outputFile
			fi	
		else
			# If initial state, make it a green box
			if [ "$initialState" == "true" ]
			then
				echo "        \"${NumNameArr[$i]}\" [label=\"${NumNameArr[$i]}\", style=filled, fillcolor=green]"  >> $outputFile
			fi

			# If final state, make it a yellow box
			if [ "$finalState" == "true" ]
			then
				echo "        \"${NumNameArr[$i]}\" [label=\"${NumNameArr[$i]}\", shape=box, style=filled, fillcolor=yellow]"  >> $outputFile
			fi
		fi # End of if [[ interesting ]]
	fi # End of if [[ !skip ]]
done
echo "{rank=same;$sameOnes}  // Put them on the same level" >> $outputFile
echo "}"  >> $outputFile