import time
from collections import defaultdict
from heapq import heappop, heappush

import numpy as np
import pygame

from .utils import (can_move, dijkstra_sum, get_state, is_deadlock, is_solved,
                    manhattan_sum, print_state)

def astar(matrix, player_pos, widget=None, visualizer=False, heuristic='manhattan'):
	"""
	Use A* algorithm to find the optimal path to solve sokoban puzzle

	Parameters:
		matrix (numpy.ndarray): sokoban puzzle matrix, 2D numpy array (height, width)
		player_pos (tuple): player position in the matrix (x, y)
		widget (Widget, optional): pygame widget to display the solution. Defaults to None.
		visualizer (bool, optional): flag to enable or disable the visualizer. Defaults to False.
		heuristic (str, optional): heuristic to use, 'manhattan' or 'dijkstra'. Defaults to 'manhattan'.

	Returns:
		tuple: solution path as a string and depth 
	"""

	# print the heuristic
	print(f'A* - {heuristic.title()} Heuristic')
	heur = '[A*]' if heuristic == 'manhattan' else '[Dijkstra]'
	shape = matrix.shape

	# initial state
	initial_state = get_state(matrix)
	initial_cost = curr_depth = 0

	# select manhattan or dijkstra heuristic
	if heuristic == 'manhattan':
		curr_cost = manhattan_sum(initial_state, player_pos, shape)
	else:
		distances = defaultdict(lambda: [])
		curr_cost = dijkstra_sum(initial_state, player_pos, shape, distances)

	# init a set to mark seen states and a heap (priority queue - min heap)
	seen = {None}
	heap = []
	
	# initial state to the heap
	heappush(heap, (initial_cost, curr_cost, initial_state, player_pos, curr_depth, ''))

	moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]
	direction = {
		(1, 0): 'D',
		(-1, 0): 'U', 
		(0, -1): 'L',
		(0, 1): 'R',
	}

	while heap:
		# check for pygame events
		if widget:
			pygame.event.pump()
		
		# pop the smallest cost node
		_, curr_cost, state, pos, depth, path = heappop(heap)

		# seen flag
		seen.add(state)

		for move in moves:
			# skip seen states and deadlocks
			new_state, move_cost = can_move(state, shape, pos, move)
			deadlock = is_deadlock(new_state, shape)
			if new_state in seen or deadlock:
				continue

			# calculate new position and cost
			new_pos = pos[0] + move[0], pos[1] + move[1]
			if heuristic == 'manhattan':
				new_cost = manhattan_sum(new_state, new_pos, shape)
			else:
				new_cost = dijkstra_sum(new_state, new_pos, shape, distances)

			# skip infinity state
			if new_cost == float('inf'):
				continue

			# push the new state onto the heap
			heappush(heap, (
				move_cost + curr_cost,
				new_cost,
				new_state,
				new_pos,
				depth + 1,
				path + direction[move],
			))

			# check if the solution is found
			if is_solved(new_state):
				print(f'{heur} Solution found!\n\n{path + direction[move]}\nDepth {depth + 1}\n')
				if widget and visualizer:
					widget.solved = True
					widget.set_text(f'{heur} Solution Found!\n{path + direction[move]}', 20)
					pygame.display.update()
				return (path + direction[move], depth + 1)
			
			# update visualizer if enabled
			if widget and visualizer:
				widget.set_text(f'{heur} Solution Depth: {depth + 1}\n{path + direction[move]}', 20)
				pygame.display.update()

	# solution not found			
	print(f'{heur} Solution not found!\n')
	if widget and visualizer:
		widget.set_text(f'{heur} Solution Not Found!\nDepth {depth + 1}', 20)
		pygame.display.update()
	return (None, -1 if not heap else depth + 1)

# Read the sokoban puzzle matrix and player position
def solve_astar(puzzle, widget=None, visualizer=False, heuristic='manhattan'):
	matrix = puzzle
	where = np.where((matrix == '*') | (matrix == '%'))
	player_pos = where[0][0], where[1][0]
	return astar(matrix, player_pos, widget, visualizer, heuristic)

if __name__ == '__main__':
	start = time.time()
	solve_astar(np.loadtxt('levels/lvl5.dat', dtype='<U1'), heuristic='dijkstra')

	# Calculate the runtime
	print(f'Runtime: {time.time() - start} seconds')
