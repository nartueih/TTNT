import time
from collections import deque

import numpy as np
import pygame

from .utils import can_move, get_state, is_deadlock, is_solved, print_state


def bfs(matrix, player_pos, widget=None, visualizer=False):
	"""
	Use Breadth-First Search to solve the Sokoban puzzle.

	Parameters:
		matrix (np.ndarray): The Sokoban puzzle, 2D numpy array. (height, width)
		player_pos (tuple): The player's position. (x, y)
		widget (Widget): The widget to display the solution. default is None. 
		visualizer (bool): Whether to visualize the solution. default is False.

	Returns:
		tuple: The solution path as a string and depth.
	"""

	print('Breadth-First Search')

	# Get the initial state
	initial_state = get_state(matrix)
	shape = matrix.shape

	# Print the initial state
	print_state(initial_state, shape)

	seen = {None}
	q = deque([(initial_state, player_pos, 0, '')])

	moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]

	curr_depth = 0
	direction = {
		(1, 0): 'D',
		(-1, 0): 'U', 
		(0, -1): 'L',
		(0, 1): 'R',
	}

	while q:
		# check for pygame events
		if widget:
			pygame.event.pump()
		
		# Get the current state, position, depth, and path from the head of the queue
		state, pos, depth, path = q.popleft()

		# tracking the depth
		if depth != curr_depth:
			print(f'Depth: {depth}')
			curr_depth = depth

		# track the seen states
		seen.add(state)

		for move in moves:
			# check valid move
			new_state, _ = can_move(state, shape, pos, move)
			deadlock = is_deadlock(new_state, shape)
			if new_state in seen or deadlock:
				continue
			
			new_pos = pos[0] + move[0], pos[1] + move[1]

			# add the new state, position, depth, and path to the tail of the queue
			q.append((
				new_state, 
				new_pos,
				depth + 1,
				path + direction[move],
			))

			# check the solution is found
			if is_solved(new_state):
				print(f'[BFS] Solution found!\n\n{path + direction[move]}\nDepth {depth + 1}\n')
				if widget and visualizer:
					widget.solved = True
					widget.set_text(f'[BFS] Solution Found!\n{path + direction[move]}', 20)
					pygame.display.update()
				return (path + direction[move], depth + 1)
			
			# update the widget and visualizer
			if widget and visualizer:
				widget.set_text(f'[BFS] Solution Depth: {depth + 1}\n{path + direction[move]}', 20)
				pygame.display.update()

	# solution not found
	print(f'[BFS] Solution not found!\n')
	if widget and visualizer:
		widget.set_text(f'[BFS] Solution Not Found!\nDepth {depth + 1}', 20)
		pygame.display.update()
	return (None, -1 if not q else depth + 1)

# get player position and call bfs
def solve_bfs(puzzle, widget=None, visualizer=False):
	matrix = puzzle
	where = np.where((matrix == '*') | (matrix == '%'))
	player_pos = where[0][0], where[1][0]
	return bfs(matrix, player_pos, widget, visualizer)

	
if __name__ == '__main__':
	# count the runtime
	start = time.time()
	root = solve_bfs(np.loadtxt('levels/lvl7.dat', dtype='<U1'))
	print(f'Runtime: {time.time() - start} seconds')
