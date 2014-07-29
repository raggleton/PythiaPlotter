#! /usr/bin/env python

"""
 Jim Henderson January 2013
 James.Henderson@cern.ch

 Usage:
 hepmc2root.py -f <Input_hepmc_file>

 PLEASE NOTE: This conversion was generated to convert hepmc 2.06.05, it may not work on other versions
              Please check the hepmc version # at the top of the hepmc file

              The units this code was built around are: GeV & mm
              Please check if this is consistent with your hepmc file


Change jets to ANTI kt 4 jet collection
"""

import os, sys, math
import ROOT as r
from ROOT import TTree, TFile, AddressOf, gROOT
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-n", dest="DO_EVENTS", type=int, help="How many events to convert, default = 100, -1 = all", default = 100)
parser.add_option("-f", dest="IN_FILE",    type=str, help="The input hepmc file you wish to convert, default = events.hepmc2g", default = "events.hepmc2g")
parser.add_option("-o", dest="OUT_FILE",   type=str, help="The output root filename, default = hepmc.root", default = "hepmc.root")

parser.add_option("-j", action="store_true", dest="all_jets", help="When building the jets, consider all jet components, not just pT > 10 MeV",         default = 0)

(options, args) = parser.parse_args()

try:
    input_file = file( options.IN_FILE, 'r')
except:
    print "\nThe input file cannot be opened, please enter a vaild .hepmc file. Exiting. \n"
    sys.exit(1)

try:
    output_file = TFile( options.OUT_FILE, "RECREATE")
except:
    print "Cannot open output file named: " + options.OUT_FILE + "\nPlease enter a valid output file name. Exiting"
    sys.exit(1)
    
output_tree = TTree("Physics", "Physics")
print "Setup complete \nOpened file " + options.IN_FILE + "  \nConverting to .root format and outputing to " + options.OUT_FILE

# Set the delta R for the jet Algorithm
R = 0.4
# Choose the jet algorithm
# 1 = kT, 0 = C/A, -1 = anti kT
J = -1


# Setup output branches
PID_v = r.vector('Int_t')()
P_X_v = r.vector('Double_t')()
P_Y_v =r.vector('Double_t')()
P_Z_v =r.vector('Double_t')()
P_T_v =r.vector('Double_t')()
E_v =r.vector('Double_t')()
M_v =r.vector('Double_t')()
Eta_v =r.vector('Double_t')()
Phi_v =r.vector('Double_t')()

Jet_pt_v =r.vector('Double_t')()
Jet_eta_v =r.vector('Double_t')()
Jet_phi_v =r.vector('Double_t')()

Vertex_x_v =r.vector('Double_t')()
Vertex_y_v =r.vector('Double_t')()
Vertex_z_v =r.vector('Double_t')()

# Create a struct which acts as the TBranch for non-vectors
gROOT.ProcessLine(\
          "struct MyStruct{\
          Int_t n_particles;\
          Double_t MET_et;\
          Double_t MET_phi;\
          Double_t Sum_et;\
          Int_t Jet_n;\
          };")
from ROOT import MyStruct

# Assign the variables to the struct
s = MyStruct() 
output_tree.Branch('n_particles',AddressOf(s,'n_particles'),'n_particles/I')
output_tree.Branch("PID",PID_v)
output_tree.Branch("P_X",P_X_v)
output_tree.Branch("P_Y",P_Y_v)
output_tree.Branch("P_Z",P_Z_v)
output_tree.Branch("P_T",P_T_v)
output_tree.Branch("E",E_v)
output_tree.Branch("M",M_v)
output_tree.Branch("Eta",Eta_v)
output_tree.Branch("Phi",Phi_v)
output_tree.Branch('Jet_n', AddressOf(s,'Jet_n'),'Jet_n/I')
output_tree.Branch("Jet_pt",Jet_pt_v)
output_tree.Branch("Jet_eta",Jet_eta_v)
output_tree.Branch("Jet_phi",Jet_phi_v)
output_tree.Branch("V_X",Vertex_x_v)
output_tree.Branch("V_Y",Vertex_y_v)
output_tree.Branch("V_Z",Vertex_z_v)
output_tree.Branch('Sum_et', AddressOf(s,'Sum_et'),'Sum_et/D')
output_tree.Branch('MET_et', AddressOf(s,'MET_et'),'MET_et/D')
output_tree.Branch('MET_phi', AddressOf(s,'MET_phi'),'MET_phi/D')

premature_exit = 0
event_number = 0
good_E = 0 # On the occurance of the first 'E', we do not want to write out an event, but we do on every other 'E' line
s.n_particles = 0
s.Sum_et = 0
s.MET_et = 0
s.MET_phi = 0
for line in input_file:
    if line.startswith("E") or line.startswith("HepMC::IO_GenEvent-END_EVENT_LISTING"):
        
        #print event_number

        if event_number == options.DO_EVENTS:   premature_exit = 1

        if event_number % 100 == 0:
            print "Processed event number: " + str(event_number)
        event_number += 1
        
        if good_E:

            # Build the MET from all neutrinos in the event
            met_px = 0
            met_py = 0
            for particle in xrange( s.n_particles ):
                this_et = E_v[ particle ] * math.fabs( math.sin( math.atan( P_T_v[ particle ] / P_Z_v[ particle ] ) ) )
                # Should Sum_et include missing et??
                s.Sum_et += this_et 
                if math.fabs(PID_v[ particle ]) == 12 or math.fabs(PID_v[ particle ]) == 14 or math.fabs(PID_v[ particle ]) == 16:
                    s.MET_et += this_et
                    met_px += P_X_v[ particle ]
                    met_py += P_Y_v[ particle ]
            s.MET_phi = math.pi/2. - math.atan( met_px / met_py )

            # Build the jets
            i_it = 0
            j_it = 0
            if not options.all_jets:
                Pseudo_jets_eta_v = []
                Pseudo_jets_phi_v = []
                Pseudo_jets_pt_v  = []
                Pseudo_jets_px_v  = []
                Pseudo_jets_py_v  = []
                Pseudo_jets_pz_v  = []

                for jet_comp in xrange( len( Eta_v ) ):
                    if P_T_v[ jet_comp ] > 10000:
                        Pseudo_jets_eta_v.append( Eta_v[ jet_comp ] )
                        Pseudo_jets_phi_v.append( Phi_v[ jet_comp ] )
                        Pseudo_jets_pt_v.append( P_T_v[ jet_comp ] )
                        Pseudo_jets_px_v.append( P_X_v[ jet_comp ] )
                        Pseudo_jets_py_v.append( P_Y_v[ jet_comp ] )
                        Pseudo_jets_pz_v.append( P_Z_v[ jet_comp ] )

            else:
                Pseudo_jets_eta_v = list( Eta_v )
                Pseudo_jets_phi_v = list( Phi_v )
                Pseudo_jets_pt_v  = list( P_T_v )
                Pseudo_jets_px_v  = list( P_X_v )
                Pseudo_jets_py_v  = list( P_Y_v )
                Pseudo_jets_pz_v  = list( P_Z_v )

            #print "Number of jet components: " + str( len( Pseudo_jets_pt_v ) )
            
            #while not( i_it == len(Pseudo_jets_pt_v) - 1 and j_it == i_it):
            while not( i_it == len(Pseudo_jets_pt_v) - 1) and not(j_it == i_it):
                new_jet = 0
                if len(Pseudo_jets_pt_v) == 0:
                    break
                for i_it in xrange( len(Pseudo_jets_pt_v) ):
                    if new_jet: break
                    for j_it in xrange( len(Pseudo_jets_pt_v) ):
                        if new_jet: break
                        if i_it == j_it: continue
                        d_phi = Pseudo_jets_phi_v[ i_it ] - Pseudo_jets_phi_v[ j_it ]
                        d_eta = Pseudo_jets_eta_v[ i_it ] - Pseudo_jets_eta_v[ j_it ]

                        if Pseudo_jets_pt_v[ i_it ] < Pseudo_jets_pt_v[ j_it ]:
                            d_ij = (Pseudo_jets_pt_v[ i_it ] ** (2 * J) ) * ( math.sqrt( d_phi * d_phi + d_eta * d_eta ) ) / R
                        else:
                            d_ij = (Pseudo_jets_pt_v[ j_it ] ** (2 * J) ) * ( math.sqrt( d_phi * d_phi + d_eta * d_eta ) ) / R

                        if d_ij < (Pseudo_jets_pt_v[ i_it ] ** (2 * J) ):
                            new_jet = 1
                            # Cluster i and j and retsart
                            new_px = Pseudo_jets_px_v[ i_it ] + Pseudo_jets_px_v[ j_it ]
                            new_py = Pseudo_jets_py_v[ i_it ] + Pseudo_jets_py_v[ j_it ]
                            new_pz = Pseudo_jets_pz_v[ i_it ] + Pseudo_jets_pz_v[ j_it ]
                            new_pt = math.sqrt( new_px ** 2 + new_py ** 2 )
        
                            new_size_p = math.sqrt( new_px ** 2 + new_py ** 2 + new_pz ** 2 )
                            new_eta = 0.5 * math.log( ( new_size_p + new_pz ) / ( new_size_p - new_pz ) )
                            new_phi = math.pi / 2. - math.atan( new_px / new_py )

                            # Make the new vectors of jets
                            temp_eta = list( Pseudo_jets_eta_v )
                            temp_phi = list( Pseudo_jets_phi_v )
                            temp_pt  = list( Pseudo_jets_pt_v )
                            temp_px  = list( Pseudo_jets_px_v )
                            temp_py  = list( Pseudo_jets_py_v )
                            temp_pz  = list( Pseudo_jets_pz_v )
                            
                            Pseudo_jets_eta_v = []
                            Pseudo_jets_phi_v = []
                            Pseudo_jets_pt_v = []
                            Pseudo_jets_px_v = []
                            Pseudo_jets_py_v = []
                            Pseudo_jets_pz_v = []
                            
                            for jet in xrange( len( temp_pt ) ):
                                if jet == i_it or jet == j_it: continue
                                Pseudo_jets_eta_v.append( temp_eta[ jet ] )
                                Pseudo_jets_phi_v.append( temp_phi[ jet ] )
                                Pseudo_jets_pt_v.append( temp_pt[ jet ] )
                                Pseudo_jets_px_v.append( temp_px[ jet ] )
                                Pseudo_jets_py_v.append( temp_py[ jet ] )
                                Pseudo_jets_pz_v.append( temp_pz[ jet ] )
                                
                            Pseudo_jets_eta_v.append( new_eta )
                            Pseudo_jets_phi_v.append( new_phi )
                            Pseudo_jets_pt_v.append(  new_pt )
                            Pseudo_jets_px_v.append(  new_px ) 
                            Pseudo_jets_py_v.append(  new_py )
                            Pseudo_jets_pz_v.append(  new_pz )


            s.Jet_n = len( Pseudo_jets_pt_v )
            for jet in xrange( s.Jet_n ):
                Jet_pt_v.push_back( Pseudo_jets_pt_v[ jet ] )
                Jet_eta_v.push_back( Pseudo_jets_eta_v[ jet ] )
                Jet_phi_v.push_back( Pseudo_jets_phi_v[ jet ] )
            
            output_tree.Fill()
            # Reset variables
            s.n_particles = 0
            s.Sum_et = 0
            s.MET_et = 0
            s.MET_phi = 0
            s.Jet_n = 0
            PID_v.clear()
            P_X_v.clear()
            P_Y_v.clear()
            P_Z_v.clear()
            P_T_v.clear()
            E_v.clear()
            M_v.clear()
            Eta_v.clear()
            Phi_v.clear()
            Jet_pt_v.clear()
            Jet_eta_v.clear()
            Jet_phi_v.clear()
            Vertex_x_v.clear()
            Vertex_y_v.clear()
            Vertex_z_v.clear()
            this_vertex_x = 0
            this_vertex_y = 0
            this_vertex_z = 0
        good_E = 1 
        
    if line.startswith("P"):
        # Check the status of this particle
        if line.split()[8] is"1":
            # We have a final state particle on this line
            s.n_particles += 1

            p_x = float(line.split()[3])
            p_y = float(line.split()[4])
            p_z = float(line.split()[5])
            
            PID_v.push_back( int(line.split()[2]) )
            P_X_v.push_back( p_x )
            P_Y_v.push_back( p_y )
            P_Z_v.push_back( p_z )
            P_T_v.push_back( math.sqrt( p_x ** 2 + p_y ** 2 ) )
            E_v.push_back( float(line.split()[6]) )
            M_v.push_back( float(line.split()[7]) )

            Vertex_x_v.push_back( this_vertex_x )
            Vertex_y_v.push_back( this_vertex_y)
            Vertex_z_v.push_back( this_vertex_z)

            # Calculate the eta (pseudorapdity):
            size_mon = math.sqrt( p_x ** 2 + p_y ** 2 + p_z ** 2 )

            eta = 0.5 * math.log( (size_mon + p_z) / (size_mon - p_z ) )
            Eta_v.push_back( eta )

            # Calculate the phi angle:

            phi = math.pi/2. - math.atan( float(line.split()[3]) / float(line.split()[4]) )
            Phi_v.push_back( phi )

    if line.startswith("V"):
        # Get the vertex information for the upcoming particles:
        this_vertex_x = float(line.split()[3])
        this_vertex_y = float(line.split()[4])
        this_vertex_z= float(line.split()[5])
        
    if premature_exit == 1:
        break

print "Successfully processed " + str( event_number - 1 ) + " events in total. Closing."
output_tree.Write()
output_file.Close()
