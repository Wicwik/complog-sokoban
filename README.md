# complog-sokoban
Author: Robert Belanec

AIS ID: belalnec6

Date: 17.10.2021

A python3 script that solves a Sokoban game represented as planning problem using minisat SAT solver.

## Input specification:
- input filename - filepath to valid sokoban map (see examples in repo)
- output filename - filepath to where you want to save output
- -s --steps (optional) - maximum number of iterations

## How to run
1. git clone https://github.com/Wicwik/complog-sokoban.git
2. cd complog-sokoban
3. python3 main.py input_filename output_filename \[-s STEPS\]

**To help:** python3 main.py -h

**Sample command:**  python3 main.py map1.txt output.txt

Input: map1.txt
```
######
#s   #
#CCCX#
#X   #
######
```
Output: output.txt (also stdout)
```
push(C0,13,19,1) move(13,7,2) move(7,8,3) move(8,9,4) move(9,10,5) move(10,16,6) move(16,22,7) move(22,21,8) move(21,20,9) push(C1,14,8,10) push(C2,15,16,11) move(15,9,12) push(C1,8,7,13)
```


