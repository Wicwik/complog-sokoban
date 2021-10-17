import subprocess
import sys
import re
import argparse

# argument parsing
parser = argparse.ArgumentParser(description='Find a solution for a Sokoban planning problem.')
parser.add_argument('input_filename',type=str, help='input map')
parser.add_argument('output_filename',type=str, help='output file')
parser.add_argument('-s','--steps',type=int, help='maximum steps')
args = parser.parse_args()

input_filename = args.input_filename
output_filename = args.output_filename

input_file = open(input_filename, 'r')

row_length = len(input_file.readline())-1

input_file.seek(0)

map_dict = {}
neigbors = []
valid_tiles = []
n_crates = 0

tile_counter = 0

x_counter = 0
s_counter = 0

for line in input_file:
	for c in line:
		if c == '#':
			map_dict[tile_counter] = '#'
		elif c == ' ':
			map_dict[tile_counter] = ' '
			valid_tiles.append(tile_counter)
		elif c == 'S':
			map_dict[tile_counter] = ['at(S,{0},0)'.format(tile_counter)]
			valid_tiles.append(tile_counter)
			s_counter += 1
		elif c == 's':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter), 'at(S,{0},0)'.format(tile_counter)]
			valid_tiles.append(tile_counter)
			x_counter += 1
			s_counter += 1
		elif c == 'X':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter)]
			valid_tiles.append(tile_counter)
			x_counter += 1
		elif c == 'C':
			map_dict[tile_counter] = ['at(C{1},{0},0)'.format(tile_counter, n_crates)]
			valid_tiles.append(tile_counter)
			n_crates += 1
		elif c == 'c':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter), 'at(C{1},{0},0)'.format(tile_counter, n_crates)]
			valid_tiles.append(tile_counter)
			x_counter += 1
			n_crates += 1
		elif c == '\n':
			continue

		tile_counter += 1

input_file.close()

for n_tile in map_dict:
	if map_dict[n_tile] != '#':
		if map_dict[n_tile+1] != '#':
			neigbors.append('next({0},{1})'.format(n_tile, n_tile+1))

		if map_dict[n_tile-1] != '#':
			neigbors.append('next({0},{1})'.format(n_tile, n_tile-1))

		if map_dict[n_tile+row_length] != '#':
			neigbors.append('next({0},{1})'.format(n_tile, n_tile+row_length))

		if map_dict[n_tile-row_length] != '#':
			neigbors.append('next({0},{1})'.format(n_tile, n_tile-row_length))


if s_counter != 1 or x_counter != n_crates:
	print('[ERROR] Invalid map. Exiting.')
	exit(1)


SAT = False
goal_iteration = 2

while not SAT:
	tmp_file = open('sokoban{0}.tmp'.format(goal_iteration-1), 'w')

	print('[INFO] Beginning of the {0}. iteration.'.format(goal_iteration-1))
	# first write statements that won't change over iterations
	for neigh in neigbors:
		tmp_file.write(neigh + '\n')

	tmp_file.write('\n')

	print('[INFO] Writing down INITIAL STATE.')
	tmp_file.write('c INITIAL STATE\n')

	for n_tile in map_dict:
		if map_dict[n_tile] != '#' and map_dict[n_tile] != ' ':
			for item in map_dict[n_tile]:
				if 'C' in item or 'S' in item:
					tmp_file.write(item + '\n')

	print('[INFO] Writing down GOAL STATE.')
	tmp_file.write('\n')
	tmp_file.write('c GOAL STATE\n')
	for n_tile in map_dict:
		if map_dict[n_tile] != '#' and map_dict[n_tile] != ' ':
			for item in map_dict[n_tile]:
				if 'X' in item:
					for ci in range(n_crates):
						if ci != (n_crates-1):
							tmp_file.write(item.replace('X', 'C{0}'.format(ci)).replace(')', ',{0}) v '.format(goal_iteration-1)))
						else:
							tmp_file.write(item.replace('X', 'C{0}'.format(ci)).replace(')', ',{0})\n'.format(goal_iteration-1)))

	print('[INFO] Writing down ACTIONS.')
	tmp_file.write('\n')
	tmp_file.write('c ACTIONS\n')
	actions = {}
	for i in range(goal_iteration):
		if i != 0:
			actions[i] = []
			tmp_file.write('c move(x,y,{0}) -> next(x,y), at(S,x,{1}), -at(C,y,{1}), at(S,y,{0}), -at(S,x,{0})\n'.format(i, i-1))
			for x in range(tile_counter):
				for y in range(tile_counter):
					if x != y and 'next({0},{1})'.format(x,y) in neigbors:
						tmp_file.write('-move({0},{1},{2}) v next({0},{1})\n'.format(x,y,i))
						tmp_file.write('-move({0},{1},{2}) v at(S,{0},{3})\n'.format(x,y,i,i-1))

						for ci in range(n_crates):
							tmp_file.write('-move({0},{1},{2}) v -at(C{4},{1},{3})\n'.format(x,y,i,i-1,ci))
						
						tmp_file.write('-move({0},{1},{2}) v at(S,{1},{2})\n'.format(x,y,i))
						tmp_file.write('-move({0},{1},{2}) v -at(S,{0},{2})\n'.format(x,y,i))
						tmp_file.write('\n')

						actions[i].append('move({0},{1},{2})'.format(x,y,i))

			tmp_file.write('\n')


	for i in range(goal_iteration):
		if i != 0:
			tmp_file.write('c push(C,y,z,{0}) -> at(S,x,{1}), next(y,z), next(x,y), -at(C,z,{1}), at(S,y,{0}), at(C,z,{0}), -at(C,y,{0}), -at(S,x,{0})\n'.format(i, i-1))
			for y in range(tile_counter):
				for z in range(tile_counter):
					if y != z and 'next({0},{1})'.format(y,z) in neigbors and 'next({0},{1})'.format(z,y) in neigbors and (y+(y-z)) in valid_tiles:
						for ci in range(n_crates):
							tmp_file.write('-push(C{5},{0},{1},{2}) v at(S,{4},{3})\n'.format(y,z,i,i-1,y+(y-z),ci))
							tmp_file.write('-push(C{3},{0},{1},{2}) v next({0},{1})\n'.format(y,z,i,ci))
							tmp_file.write('-push(C{4},{0},{1},{2}) v next({3},{0})\n'.format(y,z,i,y+(y-z),ci))
							tmp_file.write('-push(C{4},{0},{1},{2}) v at(C{4},{0},{3})\n'.format(y,z,i,i-1,ci))

							for cj in range(n_crates):
								if ci != cj:
									tmp_file.write('-push(C{4},{0},{1},{2}) v -at(C{5},{1},{3})\n'.format(y,z,i,i-1,ci,cj))
							
							tmp_file.write('-push(C{3},{0},{1},{2}) v at(S,{0},{2})\n'.format(y,z,i,ci))
							tmp_file.write('-push(C{3},{0},{1},{2}) v at(C{3},{1},{2})\n'.format(y,z,i,ci))
							tmp_file.write('-push(C{3},{0},{1},{2}) v -at(C{3},{0},{2})\n'.format(y,z,i,ci))
							tmp_file.write('-push(C{4},{0},{1},{2}) v -at(S,{3},{2})\n'.format(y,z,i,y+(y-z),ci))
							tmp_file.write('\n')

							actions[i].append('push(C{3},{0},{1},{2})'.format(y,z,i,ci))

	print('[INFO] Writing down AT LEAST ONE ACTION HAPPENS.')
	tmp_file.write('\n')
	tmp_file.write('c AT LEAST ONE ACTION HAPPENS\n')
	for i in range(goal_iteration):
		if i != 0:
			for a in actions[i]:
				if a != actions[i][-1]:
					tmp_file.write(a + ' v ')
				else:
					tmp_file.write(a + '\n')


	print('[INFO] Writing down EXCLUSIVITY.')
	tmp_file.write('\n')
	tmp_file.write('c EXCLUSIVITY\n')
	
	for i in range(goal_iteration):
		#added = []
		if i != 0:
			for a in actions[i]:
				for b in actions[i]:
					excl_str = '-' + a + ' v -' + b
					#excl_str_rev = '-' + b + ' v -' + a + '\n'
					if a != b: #and excl_str not in added and excl_str_rev not in added:
						tmp_file.write(excl_str + '\n')
						#added.append(excl_str)

	# print(actions)
	# print(len(added))

	print('[INFO] Writing down FRAME PROBLEM.')
	tmp_file.write('\n')
	tmp_file.write('c FRAME PROBLEM\n')
	for i in range(goal_iteration):
		if i != 0:
			for x in range(tile_counter):
				for a in range(tile_counter):
					for b in range(tile_counter):
						if a != b and a != x and b != x and 'move({0},{1},{2})'.format(a,b,i) in actions[i] and x in valid_tiles:
							for ci in range(n_crates):
								tmp_file.write('-at(C{5},{0},{4}) v -move({1},{2},{3}) v at(C{5},{0},{3})\n'.format(x,a,b,i,i-1,ci))

			tmp_file.write('\n')
			for x in range(tile_counter):
				for a in range(tile_counter):
					for b in range(tile_counter):
						for ci in range(n_crates):
							for cj in range(n_crates):
								if a != b and a != x and b != x and 'push(C{3},{0},{1},{2})'.format(a,b,i,ci) in actions[i] and x in valid_tiles and cj != ci:
									tmp_file.write('-at(C{5},{0},{4}) v -push(C{6},{1},{2},{3}) v at(C{5},{0},{3})\n'.format(x,a,b,i,i-1,ci,cj))

	print('[INFO] Writing down BACKGROUND.')
	tmp_file.write('\n')
	tmp_file.write('c BACKGROUND\n')
	for i in range(goal_iteration):
		if i != 0:
			for x in range(tile_counter):
				for y in range(tile_counter):
					if x != y and x in valid_tiles and y in valid_tiles:
						tmp_file.write('-at(S,{0},{2}) v -at(S,{1},{2})\n'.format(x,y,i-1))
						tmp_file.write('-at(S,{0},{2}) v -at(S,{1},{2})\n'.format(x,y,i))

						for ci in range(n_crates):
							tmp_file.write('-at(C{3},{0},{2}) v -at(C{3},{1},{2})\n'.format(x,y,i-1,ci))
							tmp_file.write('-at(C{3},{0},{2}) v -at(C{3},{1},{2})\n'.format(x,y,i,ci))


	tmp_file.close()

	proc = subprocess.Popen(['python3', 'text2dimacs.py',  'sokoban{0}.tmp'.format(goal_iteration-1)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	dimacs_file = open('sokoban{0}.dimacs'.format(goal_iteration-1), 'w')
	dimacs_file.write(proc.communicate()[0].decode("utf-8"))
	dimacs_file.close()


	proc = subprocess.Popen(['minisat', 'sokoban{0}.dimacs'.format(goal_iteration-1), 'sokoban{0}.sat'.format(goal_iteration-1)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print(proc.communicate()[0].decode("utf-8"))

	sat_file = open('sokoban{0}.sat'.format(goal_iteration-1), 'r')

	if sat_file.readline() == 'SAT\n':
		SAT = True
	else:
		if args.steps is not None and goal_iteration-1 >= args.steps:
			print('[INFO] Step parameter was specified, breaking after {0}. iteration'.format(goal_iteration-1))
			exit(0)

		sat_file.close()
		goal_iteration += 1


dimacs_file = open('sokoban{0}.dimacs'.format(goal_iteration-1), 'r')
dimacs_output = sat_file.readline()

for line in dimacs_file:
	if 'Variables' in line:
		break

actions_codes = {}
for line in dimacs_file:
	if 'move' in line or 'push' in line:
		splitted = line.split()
		actions_codes[splitted[1]] = splitted[2]

dimacs_file.close()

output = []
for code in dimacs_output.split():
	if (code[0] != '-') and code in actions_codes:
		output.append(actions_codes[code])

output_file = open(output_filename, 'w')
for out in sorted(output, key=lambda x: int(re.search(r'(\d+)(?!.*\d)',x).group())):
	output_file.write(out + ' ')
	print(out)

output_file.seek((output_file.tell()-1))
output_file.write('\n')

# move(x,y) pre x,y z <0, n>
# p+ = {next(x,y), at(S, x)} 
# p- = {at(C, y)}
# e+ = {at(S, y)}
# e- = {at(S, x)}
# move(x,y,i) -> next(x,y), at(S,x,i-1), -at(C,y,i-1), at(S,y,i), -at(S,x,i)
# -move(x,y,i) v next(x,y)
# -move(x,y,i) v at(S,x,i-1)
# -move(x,y,i) v -at(C,y,i-1)
# -move(x,y,i) v at(S,y,i)
# -move(x,y,i) v -at(S,x,i)


# push(C,y,z) pre y,z zo <0, n>
# p+ = {at(S,x), next(y,z), next(x,y), at(C,y)} x = y + (y-z)
# p- = {at(C,z)}
# e+ = {at(S,y), at(C,z)}
# e- = {at(C, y), at(S,x)}
# push(C,y,z,i) -> at(S,x,i-1), next(y,z), next(x,y), -at(C,z,i-1), at(S,y,i), at(C,z,i), -at(C,y,i), -at(S,x,i)
# -push(C,y,z,i) v at(S,x,i-1)
# -push(C,y,z,i) v next(y,z)
# -push(C,y,z,i) v next(x,y)
# -push(C,y,z,i) v at(C,y)
# -push(C,y,z,i) v -at(C,z,i-1)
# -push(C,y,z,i) v at(S,y,i)
# -push(C,y,z,i) v at(C,z,i)
# -push(C,y,z,i) v -at(C,y,i)
# -push(C,y,z,i) v -at(S,x,i)

# ak sa pohne sokoban neposunie sa krabica
# at(C,x,i-1), move(a,b,i) -> at(C,x,i) a != b != x, a,b,x z <0,n>

# ak potlaci krabicu, ostatne krabice sa neposunu
# at(C,x,i-1), push(C,a,b,i) -> at(C,x,i) a != b != x, a,b,x z <0,n>