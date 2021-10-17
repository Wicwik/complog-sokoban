# complog-sokoban
Author: Robert Belanec

AIS ID: belalnec6

Date: 17.10.2021

A python3 script that solves a Sokoban game represented as planning problem using minisat SAT solver.

## Input specification:
input filename - filepath to valid sokoban map (see examples in repo)
output filename - filepath to where you want to save output
-s --steps (optional) - maximum number of iterations

## How to run
1. git clone https://github.com/Wicwik/complog-sokoban.git
2. cd complog-sokoban
3. python3 main.py input_filename output_filename \[-s STEPS\]

**To help:** python3 main.py -h

**Sample command:**  python3 main.py map1.txt output.txt

map1.txt
######
#s   #
#CCCX#
#X   #
######


