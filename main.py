import subprocess
import sys

input_filename = sys.argv[1]

input_file = open(input_filename, 'r')

row_length = len(input_file.readline())-1

input_file.seek(0)

map_dict = {}
neigbors = []
valid_tiles = []
n_crates = 0

tile_counter = 0

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
		elif c == 's':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter), 'at(S,{0},0)'.format(tile_counter)]
			valid_tiles.append(tile_counter)
		elif c == 'X':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter)]
			valid_tiles.append(tile_counter)
		elif c == 'C':
			map_dict[tile_counter] = ['at(C{1},{0},0)'.format(tile_counter, n_crates)]
			valid_tiles.append(tile_counter)
			n_crates += 1
		elif c == 'c':
			map_dict[tile_counter] = ['at(X,{0})'.format(tile_counter), 'at(C{1},{0},0)'.format(tile_counter, n_crates)]
			valid_tiles.append(tile_counter)
			n_crates += 1
		elif c == '\n':
			continue

		tile_counter += 1

input_file.close()

# col_length = tile_counter/row_length

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

# for n_tile in map_dict:
# 	if map_dict[n_tile] != '#' and map_dict[n_tile] != ' ':
# 		for item in map_dict[n_tile]:
# 			if 'X' in item:
# 				tmp_file.write(item + '\n')

# TODO: count C and X is equal
# TODO: count S == 1


SAT = False
goal_iteration = 2

while not SAT:
	tmp_file = open('sokoban{0}.tmp'.format(goal_iteration-1), 'w')

	# first write statements that won't change over iterations
	for neigh in neigbors:
		tmp_file.write(neigh + '\n')

	tmp_file.write('\n')

	tmp_file.write('c INITIAL STATE\n')

	for n_tile in map_dict:
		if map_dict[n_tile] != '#' and map_dict[n_tile] != ' ':
			for item in map_dict[n_tile]:
				if 'C' in item or 'S' in item:
					tmp_file.write(item + '\n')

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

	tmp_file.write('\n')
	tmp_file.write('c AT LEAST ONE ACTION HAPPENS\n')
	for i in range(goal_iteration):
		if i != 0:
			for a in actions[i]:
				if a != actions[i][-1]:
					tmp_file.write(a + ' v ')
				else:
					tmp_file.write(a + '\n')


	tmp_file.write('\n')
	tmp_file.write('c EXCLUSIVITY\n')
	
	for i in range(goal_iteration):
		added = []
		if i != 0:
			for a in actions[i]:
				for b in actions[i]:
					if a != b and ('-' + a + ' v -' + b) not in added and ('-' + b + ' v -' + a) not in added:
						tmp_file.write('-' + a + ' v -' + b + '\n')
						added.append('-' + a + ' v -' + b)

	# print(actions)
	# print(len(added))

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
		sat_file.close()
		goal_iteration += 1
	

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