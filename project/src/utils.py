from heapq import heappop, heappush

import numpy as np
import pygame
import pygame_widgets 


def play_solution(solution, game, widgets, show_solution, moves):

	"""
	Play the solution path

	Parameters:
		solution (str): The solution path. (e.g: 'RULD')
		game (Game): The game instance. 
		widgets (dict): The widgets dictionary. (label, seed, visualizer, moves_label, paths)
		show_solution (bool): Whether to show the solution. 
		moves (int): The number of moves.
	
	Returns:
		int: The number of moves.
	"""
	for move in solution:
		
		# GUI
		events = pygame.event.get()
		moves += game.player.update(move)
		game.floor_group.draw(game.window)
		game.goal_group.draw(game.window)
		game.object_group.draw(game.window)
		pygame_widgets.update(events)
		widgets['label'].draw()
		widgets['seed'].draw()
		widgets['visualizer'].draw()

		# print the number of moves with 20 font size
		widgets['moves_label'].set_moves(f' Moves = {moves} ', 20)

		if show_solution:
			widgets['paths'].draw()
		pygame.display.update()

		# Delay solver
		pygame.time.delay(130)
	return moves


def print_state(state, shape):
	"""
	Print the state as a matrix

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		shape (tuple): The shape of the matrix. (height, width)

	Returns:
		None, prints the state as a matrix.
	"""
	if not state:
		return
	m, n = shape
	# convert state to matrix 2D
	matrix = np.array(list(state)).reshape(m, n)
	print(matrix)


def find_boxes_and_goals(state, shape):
	"""
	Find the boxes and goals in the state

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		shape (tuple): The shape of the matrix. (height, width)

	Returns:
		tuple: The boxes, goals, and boxes on goals. 
	"""
	_, width = shape
	boxes, goals, boxes_on_goal = [], [], []

	# box: @, goal: X, box on goal: $, player on goal: %
	# look through a character in the state, add state
	for pos, char in enumerate(state):
		if char == '@':
			boxes.append((pos // width, pos % width))
		elif char in 'X%':
			goals.append((pos // width, pos % width))
		elif char == '$':
			boxes_on_goal.append((pos // width, pos % width))
	return boxes, goals, boxes_on_goal

# get the state as a string and remove the null bytes
def get_state(matrix):
	return matrix.tobytes().decode('utf-8').replace('\x00', '')

# get Hashtable
# def get_state(matrix):
#     # Định nghĩa các giá trị đại diện cho các ký hiệu
#     value_dict = {
#         '+': 0,  # wall
#         '@': 1,  # box
#         '*': 2,  # player
#         'X': 3,  # goal
#         '$': 4,  # box on goal
#         '%': 5,  # player on goal
#         '-': 0   # empty
#     }
#     hash_value = 0
#     rows, cols = matrix.shape
#     for r in range(rows):
#         for c in range(cols):
#             symbol = matrix[r, c]
#             if symbol in value_dict:
#                 # Chuyển đổi vị trí (r, c) thành chỉ số một chiều
#                 index = r * cols + c
#                 # Tính toán giá trị hash bằng cách XOR
#                 hash_value ^= (index ^ value_dict[symbol])
#     return hash_value

# check if the state is solved
def is_solved(state):
	return '@' not in state

def manhattan_sum(state, player_pos, shape):
	"""
	Calculate the manhattan sum

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		player_pos (tuple): The player position (x,y).
		shape (tuple): The shape of the matrix. (height, width)

	Returns:
		int: The manhattan sum.
	"""
	height, width = shape
	player_x, player_y = player_pos
	boxes, goals, _ = find_boxes_and_goals(state, shape)

	# set the boxes cost = biggest possible cost = number of boxes * height * width
	boxes_cost = len(boxes) * height * width

	player_cost = 0

	# calculate the cost of the boxes
	# manhattan distance = |x1 - x2| + |y1 - y2|
	for box_x, box_y in boxes:
		# get the minimum cost of the boxes
		boxes_cost += min(
			# calculate the manhattan distance between the box and the goals
			abs(box_x - goal_x) + abs(box_y - goal_y) 
			for goal_x, goal_y in goals
		)

	# calculate the heuristic cost of the player to the boxes
	player_cost = min(
		# calculate the manhattan distance between the player and the boxes
		abs(box_x - player_x) + abs(box_y - player_y) 
		for box_x, box_y in boxes
		) if boxes else 0 # if there are no boxes, the cost is 0
	
	return boxes_cost + player_cost


def dijkstra(state, shape, box_pos=None, player_pos=None):
	"""
	Find the shortest path using Dijkstra's algorithm from a given position to all other positions in the matrix

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		shape (tuple): The shape of the matrix (height, width).
		box_pos (tuple): The box position (x,y). Defaults to None.
		player_pos (tuple): The player position (x,y). Defaults to None.

	Returns:
		np.array: dijk = A 2D array where each cell contains the shortest distance from the given position to that cell.
	"""

	height, width = shape

	# create a 2D array of infinities
	dijk = np.array([[float('inf') for _ in range(width)] for _ in range(height)])
	
	# set the player position to 0
	dijk[box_pos or player_pos] = 0

	# possible moves
	moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

	# create a heap, set the distance to 0 and add the box position if it is not None else add the player position
	heap = [(0, box_pos or player_pos)]

	# set the obstacles (can't move through)
	# if player_pos exists (caluclating the player position), obstacles = {wall} = {'+'}
	# else (caluclating the box position),  obstacles = ={wall, box, box on goal} = {'+', '@', '$'}
	obstacles = '+' if player_pos else '+@$'

	while heap:
		# pop the minimum distance
		distance, curr_pos = heappop(heap)
		# skip if the distance is greater than the stored distance
		if distance > dijk[curr_pos]:
			continue
		for move in moves:
			# get the new position
			new_x, new_y = curr_pos[0] + move[0], curr_pos[1] + move[1]
			new_pos = new_x, new_y
			# check if the new position is valid and not an obstacle
			if (1 <= new_x < height - 1 and
	   			1 <= new_y < width - 1 and
				state[new_x * width + new_y] not in obstacles):
				new_distance = distance + 1
				# if the new distance is less than the stored distance, update the distance
				if new_distance < dijk[new_pos]:
					dijk[new_pos] = new_distance
					heappush(heap, (new_distance, new_pos))
	return dijk


def dijkstra_sum(state, player_pos, shape, distances):
	"""
	calculates the dijkstra sum

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		player_pos (tuple): The player position (x,y).
		shape (tuple): The shape of the matrix. (height, width)
		distances (dict): The distances dictionary.

	Returns:
		int: The heuristic cost of (moving boxes to goals or moving the player to the neareast box).
	"""

	height, width = shape
	boxes, goals, boxes_on_goal = find_boxes_and_goals(state, shape)
	# set the boxes cost = biggest possible cost = number of boxes * height * width
	boxes_cost = len(boxes) * height * width
	player_cost = 0
	
	# calculate the shortest path from each box to each box on goal
	for box in boxes + boxes_on_goal:
		distances[box] = dijkstra(state, shape, box)

	# calculate the shortest path from the player to other points
	distances[player_pos] = dijkstra(state, shape, player_pos=player_pos)
	
	# find the minimum cost to any goal from each box
	for box in boxes:
		boxes_cost += min(distances[box][goal] for goal in goals)
	
	# calculate the minimum cost from the player to the boxes
	# if there are no boxes, the cost is 0
	player_cost = min(distances[player_pos][box] for box in boxes) if boxes else 0
	return boxes_cost + player_cost

def is_deadlock(state, shape):
	"""
	Check if the state is a deadlock

	Parameters:
		state (str): The state of the game represented as a string 
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		shape (tuple): The shape of the matrix. (height, width)
		
	Returns:
		bool: True if the state is a deadlock, False otherwise.

	Description:
		1. Corner deadlock: A box is in a corner and the two adjacent cells are walls.
		2. Double box deadlock: Two boxes are in a deadlock position.
		3. Too many boxes deadlock: There are too many boxes in a row.
	"""
	height, width = shape
	if not state or len(state) != height * width:
		return False
	
	boxes, _, _ = find_boxes_and_goals(state, shape)

	# check corner deadlock
	for bx, by in boxes:  
		box = bx * width + by
		# check surrounding positions
		if ((state[box - 1] == '+' and state[box - width] == '+') or
			(state[box + 1] == '+' and state[box + width] == '+') or
			(state[box + 1] == '+' and state[box - width] == '+') or
			(state[box - 1] == '+' and state[box + width] == '+')):
			return True
	
	# define positions around a box to check for double box positions
	double_box_positions = [
		(0, -1, -width, -width - 1),
		(0, 1, -width, -width + 1),
		(0, -1, width - 1, width),
		(0, 1, width + 1, width),
	]
	# check double box deadlock
	for bx, by in boxes:  
		box = bx * width + by
		for pos in double_box_positions:
			pos_set = set()
			for dir in pos:
				pos_set.add(state[box + dir])
			# check if surrounding celss form a deadlock
			if pos_set in ({'@', '+'}, {'@'}, {'@', '$'}, {'@', '$', '+'}):
				return True
			
	# check for too many boxes deadlock in a specific rows
	box = goal = 0
	# check the second row from the top
	for i in range(width + 1, 2 * width - 1):  
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	
	box = goal = 0
	# check the second to last row from the bottom
	for i in range(width * (height - 2) + 1, width * (height - 2) + width - 1):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	
	box = goal = 0
	# check columns in rows between the first and last rows
	for i in range(width + 1, width * (height - 1) + 1, width):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	
	box = goal = 0
	# check the last row
	for i in range(2 * width - 2, width * height - 2, width):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	return False


def can_move(state, shape, player_pos, move):
	"""
	Check if the player can move

	Parameters:
		state (str): The state of the game represented as a string
			('@': box, 'X': goal, '$': box on goal, '%': player on goal, '-': empty space, '+': wall).
		shape (tuple): The shape of the matrix. (height, width)
		player_pos (tuple): The player position (x,y).
		move (tuple): The move direction (x,y).

	Returns:
		tuple: The new state and the move cost.

	Description:
		1. Target position is a wall: can't move.
		2. Target position is an empty space or goal: move the player. move cost = 3
		3. Target position is a box:
			- After the box is a wall or other box: can't move.
			- After the box is an empty space or goal: move the box. 
			move cost = 0 if the box is on goal, 2 otherwise.
	"""
	new_state = list(state)
	x, y = player_pos
	_, width = shape
	move_cost = 0

	# get the target position and the box target position
	target = x + move[0], y + move[1]
	boxtarget = x + move[0] * 2, y + move[1] * 2
	# convert the 2D position to 1D
	curr1d = x * width + y
	target1d = target[0] * width + target[1]
	boxtarget1d = boxtarget[0] * width + boxtarget[1]

	if state[target1d] == '+':
		# target position = wall -> can't move
		return None, move_cost
	elif state[target1d] in '-X':
		# target position = empty space or goal -> move the player
		new_state[curr1d] = '-' if new_state[curr1d] == '*' else 'X'	# update the player's previous position
		new_state[target1d] = '*' if new_state[target1d] == '-' else '%'	# update the target position
		move_cost = 3	# move cost onto an empty space or goal = 3
	elif state[target1d] in '@$':
		# target position = box
		if state[boxtarget1d] in '+@$':
			# after the box is wall or other box -> can't move
			return None, move_cost
		elif state[boxtarget1d] in '-X':
			# after the box is empty space or goal -> move the box
			new_state[boxtarget1d] = '@' if new_state[boxtarget1d] == '-' else '$'	# move the box to the new position
			new_state[target1d] = '*' if new_state[target1d] == '@' else '%'	# update the box's original position
			new_state[curr1d] = '-' if new_state[curr1d] == '*' else 'X'	# update the player's previous position
			move_cost = 0 if new_state[boxtarget1d] == '$' else 2	# move cost = 0 if the box is on goal, 2 otherwise
	return ''.join(new_state), move_cost
