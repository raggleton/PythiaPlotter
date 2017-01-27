************************************************
Some Theory: Graphs and Particle Representations
************************************************

This is a brief introduction to graphs, some terminology, and how particle event trees can be represented by a graph.

Basics
======

A graph is composed of a set of **nodes**, along with **edges** which connect those nodes.
An example of a simple graph is shown below.

.. graphviz::

   graph foo {
      rankdir="LR";
      A -- B;
      A -- C;
   }

Edges may have a **direction** associated with them; in this case we have a **directed graph** or digraph.
An example of a digraph is shown below.

.. graphviz::

   digraph foo {
      rankdir="LR";
      nodesep=1;
      A -> B [label="Edge 1"];
      A -> C [label="Edge 2"];
   }

A directed edge has an **outgoing** node (the one it leaves) and an **incoming** node (the one it is going into).
In the example, Edge 1 has outgoing node A, and incoming node B, whilst Edge 2 has outgoing node A and incoming node C.

Particles and Graphs
====================

A particle event is characterised by the production and decay of particles; for example two gluons combine to make a Higgs boson, or a pion decays to two photons.
Therefore, there are **relationships** between these particles, which we can denote using graphs.
Physicists are already used to this without realising it: a Feynman diagram (see below) is a graph, where each particle is represented by an edge, and a node with incoming and outgoing particles indicates some interaction (a **vertex**).

